TMP_DIR = tmp
BOOMER_INPUT_DIR = boomer_input
BOOMER_OUTPUT_DIR = boomer_output

ALL_RUNS=no_mappings mondo_exact mondo_all 

$(TMP_DIR)/ $(TMP_DIR)/no_mappings/ $(BOOMER_INPUT_DIR)/no_mappings/ $(BOOMER_OUTPUT_DIR)/no_mappings/ $(TMP_DIR)/mondo_exact/ $(BOOMER_INPUT_DIR)/mondo_exact/ $(BOOMER_OUTPUT_DIR)/mondo_exact/ $(TMP_DIR)/mondo_all/ $(BOOMER_INPUT_DIR)/mondo_all/ $(BOOMER_OUTPUT_DIR)/mondo_all/ :
	mkdir -p $@

.PHONY: all
all: prepare-data boomer
	make reports # Needs to be run like this, because the jsons are unknown before the boomer run

.PHONY: prepare-data
prepare-data: $(patsubst %, prepare-data-%, $(ALL_RUNS))

.PHONY: reports
reports: $(patsubst %, reports-%, $(ALL_RUNS))


.PHONY: prepare-data-no_mappings
prepare-data-no_mappings: $(BOOMER_INPUT_DIR)/no_mappings/combined.ptable.tsv $(BOOMER_INPUT_DIR)/no_mappings/prefix.yaml $(BOOMER_INPUT_DIR)/no_mappings/symbiont-merged-all.owl 

.PHONY: prepare-data-mondo_exact
prepare-data-mondo_exact: $(BOOMER_INPUT_DIR)/mondo_exact/combined.ptable.tsv $(BOOMER_INPUT_DIR)/mondo_exact/prefix.yaml $(BOOMER_INPUT_DIR)/mondo_exact/symbiont-merged-all.owl 

.PHONY: prepare-data-mondo_all
prepare-data-mondo_all: $(BOOMER_INPUT_DIR)/mondo_all/combined.ptable.tsv $(BOOMER_INPUT_DIR)/mondo_all/prefix.yaml $(BOOMER_INPUT_DIR)/mondo_all/symbiont-merged-all.owl 


.PHONY: boomer
boomer: $(patsubst %, boomer-%, $(ALL_RUNS))

.PHONY: clean
clean:
	rm -rf ./$(BOOMER_OUTPUT_DIR)/*
	rm -rf ./$(BOOMER_INPUT_DIR)/*
	rm -rf ./$(TMP_DIR)/*

.PHONY: reset_boomer_output
reset_boomer_output:
	rm -rf ./$(BOOMER_OUTPUT_DIR)/*

#####################
### Dependencies ####
#####################

.PHONY: sssom
sssom:
	echo "skipping.."
#	python3 -m pip install --upgrade pip setuptools && python3 -m pip install --upgrade --force-reinstall git+https://github.com/mapping-commons/sssom-py.git@curie_detection_patch
#	python3 -m pip install --upgrade pip setuptools && python3 -m pip install --upgrade --force-reinstall sssom==0.3.7

#####################
## Ontologies #######
#####################

ONTOLOGIES= mondo omim doid ordo 

ALL_ONTOLOGIES=$(patsubst %, $(TMP_DIR)/%.owl, $(ONTOLOGIES))


$(TMP_DIR)/mondo.owl: | $(TMP_DIR)/
	wget http://purl.obolibrary.org/obo/mondo.owl -O $@

$(TMP_DIR)/omim.owl: | $(TMP_DIR)/
	wget https://github.com/monarch-initiative/mondo-ingest/releases/download/v2022-04-26/omim.owl -O $@

$(TMP_DIR)/doid.owl: | $(TMP_DIR)/
	wget https://github.com/monarch-initiative/mondo-ingest/releases/download/v2022-04-26/doid.owl -O $@

$(TMP_DIR)/ordo.owl: | $(TMP_DIR)/
	wget https://github.com/monarch-initiative/mondo-ingest/releases/download/v2022-04-26/ordo.owl -O $@


$(TMP_DIR)/symbiont-merged-all.owl: $(ALL_ONTOLOGIES)
	robot merge $(addprefix -i , $^) --output $@

$(BOOMER_INPUT_DIR)/%/symbiont-merged-all.owl: $(TMP_DIR)/symbiont-merged-all.owl
	cp $< $@

#####################
## Mappings #########
#####################

ALL_MAPPINGS=$(TMP_DIR)/empty.sssom.tsv $(TMP_DIR)/mondo.sssom.tsv $(TMP_DIR)/mondo_all.sssom.tsv 


$(TMP_DIR)/empty.sssom.tsv: ../../mappings/empty.sssom.tsv | $(TMP_DIR)/
	cp $< $@

$(TMP_DIR)/mondo.sssom.tsv: ../../mappings/mondo.sssom.tsv | $(TMP_DIR)/
	cp $< $@

$(TMP_DIR)/mondo_all.sssom.tsv: ../../mappings/mondo_all.sssom.tsv | $(TMP_DIR)/
	cp $< $@


$(BOOMER_INPUT_DIR)/%/combined.sssom.tsv $(BOOMER_INPUT_DIR)/%/prefix.yaml: $(ALL_MAPPINGS) | $(BOOMER_INPUT_DIR)/%/
	python $(HOME_DIR)/scripts/gen_boomer_input.py run \
		--source-location $(TMP_DIR) \
		--target-location $(BOOMER_INPUT_DIR)/$* \
		--config ../mondo-omim-ordo-do.symbiont.yaml

$(BOOMER_INPUT_DIR)/%/combined.ptable.tsv: $(BOOMER_INPUT_DIR)/%/combined.sssom.tsv
	sssom ptable $< -o $@

#####################
## Boomer ###########
#####################


boomer-no_mappings: | $(BOOMER_OUTPUT_DIR)/no_mappings/
	boomer --ptable $(BOOMER_INPUT_DIR)/no_mappings/combined.ptable.tsv \
		--ontology $(BOOMER_INPUT_DIR)/no_mappings/symbiont-merged-all.owl \
		--prefixes $(BOOMER_INPUT_DIR)/no_mappings/prefix.yaml \
		--output $(BOOMER_OUTPUT_DIR)/no_mappings/boomer_output \
		--window-count 1 \
		--exhaustive-search-limit 15 \
		--runs 1 \ 
	find $(BOOMER_OUTPUT_DIR)/no_mappings -name "*.json" -type 'f' -size -500c -delete # Hack for removing individual singleton json files.

boomer-mondo_exact: | $(BOOMER_OUTPUT_DIR)/mondo_exact/
	boomer --ptable $(BOOMER_INPUT_DIR)/mondo_exact/combined.ptable.tsv \
		--ontology $(BOOMER_INPUT_DIR)/mondo_exact/symbiont-merged-all.owl \
		--prefixes $(BOOMER_INPUT_DIR)/mondo_exact/prefix.yaml \
		--output $(BOOMER_OUTPUT_DIR)/mondo_exact/boomer_output \
		--window-count 1 \
		--exhaustive-search-limit 10 \
		--runs 1 \ 
	find $(BOOMER_OUTPUT_DIR)/mondo_exact -name "*.json" -type 'f' -size -500c -delete # Hack for removing individual singleton json files.

boomer-mondo_all: | $(BOOMER_OUTPUT_DIR)/mondo_all/
	boomer --ptable $(BOOMER_INPUT_DIR)/mondo_all/combined.ptable.tsv \
		--ontology $(BOOMER_INPUT_DIR)/mondo_all/symbiont-merged-all.owl \
		--prefixes $(BOOMER_INPUT_DIR)/mondo_all/prefix.yaml \
		--output $(BOOMER_OUTPUT_DIR)/mondo_all/boomer_output \
		--window-count 1 \
		--exhaustive-search-limit 10 \
		--runs 1 \ 
	find $(BOOMER_OUTPUT_DIR)/mondo_all -name "*.json" -type 'f' -size -500c -delete # Hack for removing individual singleton json files.


#####################
## Reports ##########
#####################

%.dot: %.json
	og2dot.js -s ../../config/boomer-style.json $< >$@ 
%.png: %.dot
	test `wc -c <$<` -gt 650000 || dot $< -Tpng -Grankdir=BT >$@


JSONS_NO_MAPPINGS=$(wildcard $(BOOMER_OUTPUT_DIR)/no_mappings/boomer_output/*.json)
PNGS_NO_MAPPINGS=$(patsubst %.json, %.png, $(filter-out singletons, $(JSONS_NO_MAPPINGS)))

.PHONY: reports-no_mappings
reports-no_mappings: $(PNGS_NO_MAPPINGS)

JSONS_MONDO_EXACT=$(wildcard $(BOOMER_OUTPUT_DIR)/mondo_exact/boomer_output/*.json)
PNGS_MONDO_EXACT=$(patsubst %.json, %.png, $(filter-out singletons, $(JSONS_MONDO_EXACT)))

.PHONY: reports-mondo_exact
reports-mondo_exact: $(PNGS_MONDO_EXACT)

JSONS_MONDO_ALL=$(wildcard $(BOOMER_OUTPUT_DIR)/mondo_all/boomer_output/*.json)
PNGS_MONDO_ALL=$(patsubst %.json, %.png, $(filter-out singletons, $(JSONS_MONDO_ALL)))

.PHONY: reports-mondo_all
reports-mondo_all: $(PNGS_MONDO_ALL)


include custom.Makefile