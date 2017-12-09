import logging
import json
import sys
import random
import multiprocessing as mp
import datetime as dt

import click
import click_log

from . import core

logger = logging.getLogger(__name__)
click_log.basic_config(logger)


@click.group()
@click_log.simple_verbosity_option(logger=logger)
def cli():
    pass


def printer(q):
    while True:
        batch = q.get()

        if batch is None:
            break

        for item in batch:
            print(*item, sep=',')

        sys.stdout.flush()


def parse_tweet_json(sample=1):
    for line in sys.stdin:
        if random.random() > sample:
            continue

        try:
            yield json.loads(line)
        except json.JSONDecodeError:
            pass


@cli.command()
@click.option('--source', default=None, help='Tweet source.')
@click.option('--topic-file', type=click.File(), default='topics.json')
@click.option('--ngram-length', default=3)
@click.option('--keep-spam', is_flag=True)
@click.option('--language', default=None, type=str)
@click.option('--extract-retweets', is_flag=True)
@click.option('--keep-retweets', is_flag=True)
@click.option('--feedback-file', type=click.File())
@click.option('--negative-distance-threshold', default=0.8)
@click.option('--sample', default=1.0)
@click.option('--topic-filter', type=click.File())
@click.option('--workers', '-j', default=max(mp.cpu_count() - 2, 1), envvar='GUNDOG_WORKERS')
def point(source, extract_retweets, language, ngram_length, keep_spam, topic_file, keep_retweets, feedback_file, negative_distance_threshold, sample, topic_filter, workers):
    random.seed(30)

    topic_filter = set(l.strip() for l in topic_filter)

    topics = [t for t in json.load(topic_file) if t['topid'] in topic_filter]

    assert keep_spam

    judged_tweets = set()
    qrels = {}
    for line in feedback_file:
        rts_id, _, tweet_id, judgment, timestamp = line.split()
        tweet_id = int(tweet_id)
        judgment = int(judgment)
        timestamp = int(timestamp)

        if judgment >= 0:
            judged_tweets.add(tweet_id)
            qrels[rts_id, tweet_id] = 1 <= judgment <= 2

    tweets = (
        t for t in parse_tweet_json(sample=sample)
        if 'id' in t and (
            t['id'] in judged_tweets or (
                (t.get('lang', language) == language)
                and (keep_spam or not t.is_spam)
                and (keep_retweets or not t.get('retweeted_status'))
            )
        )
    )

    printer_q = mp.Queue(maxsize=1)
    printer_p = mp.Process(target=printer, args=(printer_q,))
    printer_p.start()

    workers_num = max(workers, 1)
    topics_by_worker = {}
    for i, topic in enumerate(topics):
        topics_by_worker.setdefault((i % workers_num), []).append(topic)

    workers = []
    for topics in topics_by_worker.values():

        in_q = mp.Queue(maxsize=1)
        worker = mp.Process(
            target=core.point,
            kwargs=dict(
                in_q=in_q,
                out_q=printer_q,
                topics=topics,
                qrels=qrels,
                negative_distance_threshold=negative_distance_threshold,
                ngram_length=ngram_length,
            ),
        )
        worker.start()

        workers.append((topic['topid'], in_q, worker))

    try:
        batch = []
        for tweet in tweets:

            task = tweet.get('long_text') or tweet['text'], tweet['id'], dt.datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S %z %Y').isoformat()
            batch.append(task)

            if len(batch) > 1000:
                for _, in_q, _ in workers:
                    in_q.put(batch)
                batch = []
        else:
            if batch:
                for _, in_q, _ in workers:
                    in_q.put(batch)

    finally:
        for _, in_q, w in workers:
            in_q.put(None)
            in_q.close()
            in_q.join_thread()

            w.join()

        printer_q.put(None)
        printer_q.close()
        printer_q.join_thread()

        printer_p.join()

@cli.command('prepare-feedback')
@click.option('--feedback-file', type=click.File())
@click.option('--mode', type=click.Choice(['majority', 'some', 'all']))
def prepare_feedback(feedback_file, mode):
    feedback = {}

    for line in feedback_file:

        values = line.split()

        if len(values) == 5:
            topic, user, tweet_id, judgment, timestamp = values
        else:
            topic, user, tweet_id, judgment = values
            timestamp = 0

        tweet_id = int(tweet_id)
        judgment = int(judgment)
        timestamp = int(timestamp)

        feedback.setdefault(topic, {}).setdefault(tweet_id, []).append((user, judgment, timestamp))

    for topic, topic_data in feedback.items():
        for tweet_id, judgments  in topic_data.items():

            relevant = 0
            non_relevant = 0
            for _, j, _ in judgments:
                if j == 0:
                    non_relevant += 1
                elif 1 <= j <= 2:
                    relevant += 1

            if not relevant and not non_relevant:
                continue

            judgment = None
            if mode == 'majority' and relevant != non_relevant:
                judgment = 1 if relevant > non_relevant else 0
            elif mode == 'all':
                judgment = 1 if not non_relevant else 0
            elif mode == 'some':
                judgment = 1 if relevant else 0

            if judgment is not None:
                print(topic, mode, tweet_id, judgment, 0)
