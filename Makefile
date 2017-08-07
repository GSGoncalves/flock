PRODUCE = bin/python src/produce/produce
POULTRY = bin/poultry
TWARC = bin/twarc
TWEET_SORT = /Users/Shared/dnm11/tweet-sort/target/appassembler/bin/sort-pool

UBLOG_15_APRIL = tweets/hydrate/2015-04-04.through.2014-04-10
UBLOG_15_APRIL_EN = ${UBLOG_15_APRIL}_EN

.PHONY: insert hydrate share ger_user_ids ublogen

insert: $(patsubst tweets/hydrate/%.gz,tweets/db/%.inserted,$(wildcard tweets/hydrate/*/*.gz))

hydrate: $(patsubst tweets/share/%.txt,tweets/hydrate/%.gz,$(wildcard tweets/share/*/*.txt))

share: $(patsubst tweets/select/%.gz,tweets/share/%.txt,$(wildcard tweets/select/*/*))

get_user_ids:
	bin/flock config query_user_ids --poultry-config parts/etc/poultry.cfg --clusters $F

${UBLOG_15_APRIL_EN}/%:
	zcat $(patsubst ${UBLOG_15_APRIL_EN}/%,${UBLOG_15_APRIL}/%,$@) |\
	${POULTRY} filter \
	--config filters/en.cfg \
	--filters filter:en |\
	gzip > $@

# Filters the English tweets from the Ublog 2015 April collection into a separate collection.
ublogen: $(patsubst ${UBLOG_15_APRIL}/%,${UBLOG_15_APRIL_EN}/%,$(wildcard ${UBLOG_15_APRIL}/*.gz))

tweets/share/%.txt: tweets/select/%.gz
	zcat $< | ${POULTRY} show -t {t.id} > $@

tweets/hydrate/RTS16/qrelsfile.gz: rts/16/eval_qrelsfile
	cat $< | cut -d' ' -f3 | ${TWARC} hydrate - | gzip > $@

tweets/hydrate/%.gz: tweets/share/%.txt
	cat $< | ${TWARC} hydrate - | gzip > $@

rts/16/pools-sorted/%: rts/16/pools/%
	${TWEET_SORT} $< |  tac > $@

rts/16/qrels-sorted: $(patsubst rts/16/pools/%,rts/16/pools-sorted/%,$(wildcard rts/16/pools/*))
	cat rts/16/pools-sorted/* > $@
