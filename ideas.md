Introduction
============

Suppose we have a huge collection of tweets dedicated to some event, for example Olympics. Clearly, we can't read them all to get in insight of what's going on. Can we extract computationally a meaningful (graphical) summary?

Data collections
----------------

### Brexit

Fitering criteria: everything that contains the string "brexit".

#### Hypotheses

* We should be able to see two groups of tweets: the ones that agains leaving the EU and the ones that are for.
* There should be corresponding hashtags.
* We might see general sentiment.
  * The sentiment should correlate witht he referendum result per region inside fo the UK.
  * There might be difference in sentiment between EU and Non-EU countries.
* Since we can retrieve named entities, we should be able to see polititians that belong to their camp.
* Since we have link information, we should be able to show what newsites are "for" and what are "against", or rather what's the user percepion of them.

### Olympics

Olympic tweets are the tweets that contain the string 'olympic' or are witten by/mention the user @Olympics. Hopefully, this data is more language diverse then brexit.

#### Hypotheses

* We should be able to see clusters that correspond to different sports/athletes.
* If we track sentiments of the tweets about some finals, the tweets from the winning country should have positive sentiment.

### Latvia

The tweets collected from Latvia should contrast the Latvian majority with the Russian minority. The goal is to see what the interests of the two groups are, for example their reaction to the news.

#### Hypotheses

* Two distinc users. The distinction is based on the ethnical backgound.
* Various/similar interests? Do the groups listen to same artists, watch same movies, etc.
* What are the most discussed topics and are they percieved differently? E.g. brexit might have been percieved equally along the groups, but the attitute to Ukrain might vary.
* **TODO** process large cultural events: festivals or concerts of the famous bands. This might be only done in the summer 2017.
* **TODO** compare the tweets in December versus the ones in January. We should capture tweets related to the Christmas, the Latvian part of the community should

#### Data collection

The first step is to include twitter accounts of the main media companies. Collect the data from the largest cities. Look for the most popular users and include them to the final (second) data collection step.

Events of interest:

* Celebrations of Riga, end of August,
* Staro Riga,
* Museum night,
* Major natoinal celebrations, e.g, November 18,
* Cultural events: both Christmas, the New Year,
* Controversial celebrations: 8th of March, 9th of May, 16th of March,
* The beginning and the end of the school year: 1st of September, 31 of May, final exams at schools.

**TODO:**
* Do we need to balance the number of Latvian speaking users and Russian speaking users?
* Should the ratio of the different languages correspond to the demographic data?

#### Aligment of tweets in various languages

The challenge is to map data in two, or maybe even more languages. To link the tweets from the two languages of interests news articles might be useful as most media websites have two dedicated versions. If we have an url of a Russian news item, it should be possible to retrieve a similar Latvian article.

Hashtags might do their job!

#### Study 1: keyword analysis

Take the keywords disscussed in Wierzbicka (1997, page 26). Translate them to Latvia and Russian. See what their frequency ranks are, do they correlate?

Randomly sample 100 words from Latvian and Russian tweets (sampling frequency might depend on rank, so we get a portion of frequent words, a portion of medium frequent words and some rarely used words). Come up with the translations of Latvian words to Russian and for Russian words to Latvian. Note that this is a bit naive and optimistic. Again, see how frequency ranks of word pairs correlate.

Given a pair of words (taken either from Wierzbicka's list of our sample), for each word retrieve the top 5 distributional neighbours in that language. Measure the correspondence between the Latvian and Russian neighbours. The correpondance judgements should be crowdsourced.

These two experiments (frequency ranks and neighbours overlap) will identify words that are used similarly and differently.

Another contribution is the construction of a bilingual corpus.

#### Relevant materials

* http://www.diena.lv/dienas-zurnali/sestdiena/loliga-valoda-14149966
* http://liva.online/dr-sc-comm/publikacijas/
* http://www.la.lv/latvijas-politiskais-tviteris-mazs-bet-nikns-la-lv-tvitertops/
* https://twitter.com/thedansimonson/status/794207087228162048 Rudra et al.: understanding codeswitching behavior in Hindi-English bilinguals
* http://nodalida2017.se/
* https://sites.google.com/site/nlpandcss/home
* Wierzbicka, Anna. Understanding cultures through their key words: English, Russian, Polish, German, and Japanese. Vol. 8. Oxford University Press, 1997.
* Kristen Johnson, Dan Goldwasser Identifying Stance by Analyzing Political Discourse on Twitter. In Proceedings of the First Workshop on NLP and Computational Social Science, Austin, Texas, 2016.
* Sunghwan Mac Kim, Stephen Wan, Cecile Paris, Jin Brian, Bella Robinson The Effects of Data Collection Methods in Twitter. In Proceedings of the First Workshop on NLP and Computational Social Science, Austin, Texas, 2016.

## Other datasets

There are some small collections at https://github.com/dimazest/sw-twitter:

* koninginnedag: Queen's day 2012
* olympics: London 2012
* pinkpop: Pinkpop 2012
* uefa_euro: UEFA Euro 2012

# The model

The first idea is to apply doc2vec to a collection. The main goal is to get distributed representation of tweets, so later we could cluster them and see whether tweets are organised into meaningful groupings.

doc2vec takes labeled documents as in input. In our case, documents are tweets and labels are any metadata we could come up with. The labels could be:

* ✓ tweet id
* ✓ hashtags
* ✓ the screen name of the author
* ✓ user mentions
* ✓ URLs that are in the tweet
  * expand urls, so https://t.co/IQGSj1V3pU becomes http://www.wsj.com/articles/boris-johnson-emerges-as-big-winner-in-brexit-vote-1466740369?mod=e2tw
  * It ight be a good idea to split an url to several parts, so https://www.theguardian.com/travel/2016/aug/03/10-best-outdoor-swimming-holidays-around-world-italy-france-greece becomes:
    * ✓ the domain (www.theguardian.com), it is hostname in the urlparse terminology.
    * the rest of the url, but split by / (travel, 2016, aug, 03, 10-best...)
    * maybe also split the parts by '-'.
* geo information, pobably as a sring (e.g. Berlin, Germany).
* creation time
  Possible formats are (we should have all of them):
  * %Y-%m-%d-%H
  * %Y-%m
  * %d to compare days
  * %H to compare hours
  * week number
  * week day number
  * working days and weekends
* language (from the tweet json object)
* named entities (from corenlp)

The good point is that we can also get a distributed representation of the labels, so we could in prinicple cluster hashtags, or compare websites.

## The (visual) reports

Let say we want to map the hastags. We can show different clusters and see whether they make sense. In the case of #brexit, there shoule be a cloud of the #leave tweets and a cloud of the #remain tweets. Moreover, since we now hashtag counts, we could estimate density function in the space. This estimation should show us how important a cluster is. For example, there might be a very distinctive cluster, that, however appears in a very small number of tweets. This also should help us to visually show wether there are more #leave or #remain tweets.

Plot dates, for example, of the weeks before and after the referendum, show the closest hashtags around them.

## Technical details

A tweet collection is stored in a `.gz` archive that contain tweet encoded with JSON. We can pump a collection into a PosgreSQL database for further analysis as it natively supports json and allows to index fields inside of a JSON blob.

The metadata that does not come from Twitter, for example named entities, or sentiment can be stored in another fiels either as JSON or in separate columns.

### Some performance data

4.9M Brexit tweets from 24-25 of July are sampled by taking everyph 40th tweet making a selection of 122K tweets:

``` bash

zcat /homes/dm303/poultry/data/brexit/2016-06-2{4,5}-* | sed -n '1p;0~40p' | gzip > data/brexit.sample.122K/brexit.sample.gz

```

Reading the collection of 122K tweets and inserting it into an sqlalchemy session took 2 minutes and 21 seconds. Session commit took 3 mitutes and 37 seconds. Note that the database is stored on a network share.

81456 of tweets are in English, 3601 are in Italian and 2641 are in German, according to Twitter.

Useful links:
* http://docs.sqlalchemy.org/en/rel_1_0/orm/query.html?highlight=yield_per#sqlalchemy.orm.query.Query.yield_per
* http://bedquiltdb.github.io/v2.html
* https://www.postgresql.org/message-id/20160930185801.38654a1c%40e754
* http://grafana.org/
* http://alembic.zzzcomputing.com/en/latest/

Initial experiment
------------------

Take a ~4M sample of #brexit tweets during 23-24 July. See:
* how long it is to pump data to the database (1h 40m?),
* how long it takes to analyse the data with the CoreNLP tools.

**TODO:** Have a look to the making sense of twitter tutorial at ACL.

# Getting up and running

## Data setup

* `tweets/select` the tweets that are collected from the streaming api. This step *creates* the corpus. These files are not supposed to be shared. `poultry.cfg` is the config file.
* `tweets/share` the IDs of the tweets. They are meant to be shared.
* `tweets/hydrate` the hydrated tweets.

# Relevant materials
* http://www.journals.elsevier.com/computers-and-electrical-engineering/call-for-papers/special-section-on-new-trends-in-humanistic-informatics
* https://medium.com/@swainjo/us-presidential-election-2016-twitter-analysis-7596606853e5#.u71p5nuk3
* https://scholar.google.com/citations?hl=en&vq=eng_databasesinformationsystems&view_op=list_hcore&venue=Yqny2grKwjoJ.2015

## Corpus construction
* https://hal.archives-ouvertes.fr/hal-01323274/document
* http://ifarm.nl/erikt/papers/clin2013.pdf
