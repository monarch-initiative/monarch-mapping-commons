TMP_DIR = tmp
BOOMER_INPUT_DIR = boomer_input
BOOMER_OUTPUT_DIR = boomer_output

ALL_RUNS=no_mappings exact_match_only all_precise all 

$(TMP_DIR)/ $(TMP_DIR)/no_mappings/ $(BOOMER_INPUT_DIR)/no_mappings/ $(BOOMER_OUTPUT_DIR)/no_mappings/ $(TMP_DIR)/exact_match_only/ $(BOOMER_INPUT_DIR)/exact_match_only/ $(BOOMER_OUTPUT_DIR)/exact_match_only/ $(TMP_DIR)/all_precise/ $(BOOMER_INPUT_DIR)/all_precise/ $(BOOMER_OUTPUT_DIR)/all_precise/ $(TMP_DIR)/all/ $(BOOMER_INPUT_DIR)/all/ $(BOOMER_OUTPUT_DIR)/all/ :
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

.PHONY: prepare-data-exact_match_only
prepare-data-exact_match_only: $(BOOMER_INPUT_DIR)/exact_match_only/combined.ptable.tsv $(BOOMER_INPUT_DIR)/exact_match_only/prefix.yaml $(BOOMER_INPUT_DIR)/exact_match_only/symbiont-merged-all.owl 

.PHONY: prepare-data-all_precise
prepare-data-all_precise: $(BOOMER_INPUT_DIR)/all_precise/combined.ptable.tsv $(BOOMER_INPUT_DIR)/all_precise/prefix.yaml $(BOOMER_INPUT_DIR)/all_precise/symbiont-merged-all.owl 

.PHONY: prepare-data-all
prepare-data-all: $(BOOMER_INPUT_DIR)/all/combined.ptable.tsv $(BOOMER_INPUT_DIR)/all/prefix.yaml $(BOOMER_INPUT_DIR)/all/symbiont-merged-all.owl 


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

ONTOLOGIES= mondo icd10cm 
ONTOLOGY_PREFIXES= MONDO ICD10CM 

ALL_ONTOLOGIES=$(patsubst %, $(TMP_DIR)/%.owl, $(ONTOLOGIES))


$(TMP_DIR)/mondo.owl: | $(TMP_DIR)/
	wget http://purl.obolibrary.org/obo/mondo.owl -O $@

$(TMP_DIR)/icd10cm.owl: | $(TMP_DIR)/
	wget http://purl.obolibrary.org/obo/icd10cm.owl -O $@


$(TMP_DIR)/symbiont-merged-all.owl: $(ALL_ONTOLOGIES)
	robot merge $(addprefix -i , $^) --output $@

$(BOOMER_INPUT_DIR)/%/symbiont-merged-all.owl: $(TMP_DIR)/symbiont-merged-all.owl
	cp $< $@

#####################
## Mappings #########
#####################

ALL_MAPPINGS=$(TMP_DIR)/empty.sssom.tsv $(TMP_DIR)/mondo_hasdbxref_icd10cm.sssom.tsv $(TMP_DIR)/mondo_exactmatch_icd10cm.sssom.tsv $(TMP_DIR)/mondo_narrowmatch_icd10cm.sssom.tsv $(TMP_DIR)/mondo_broadmatch_icd10cm.sssom.tsv $(TMP_DIR)/ncit_icd10_2017.sssom.tsv 


$(TMP_DIR)/empty.sssom.tsv: | $(TMP_DIR)/
	wget https://raw.githubusercontent.com/mapping-commons/mapping-commons.github.io/main/mappings/empty.sssom.tsv -O $@

$(TMP_DIR)/mondo_hasdbxref_icd10cm.sssom.tsv: | $(TMP_DIR)/
	wget https://raw.githubusercontent.com/monarch-initiative/mondo/master/src/ontology/mappings/mondo_hasdbxref_icd10cm.sssom.tsv -O $@

$(TMP_DIR)/mondo_exactmatch_icd10cm.sssom.tsv: | $(TMP_DIR)/
	wget https://raw.githubusercontent.com/monarch-initiative/mondo/master/src/ontology/mappings/mondo_exactmatch_icd10cm.sssom.tsv -O $@

$(TMP_DIR)/mondo_narrowmatch_icd10cm.sssom.tsv: | $(TMP_DIR)/
	wget https://raw.githubusercontent.com/monarch-initiative/mondo/master/src/ontology/mappings/mondo_narrowmatch_icd10cm.sssom.tsv -O $@

$(TMP_DIR)/mondo_broadmatch_icd10cm.sssom.tsv: | $(TMP_DIR)/
	wget https://raw.githubusercontent.com/monarch-initiative/mondo/master/src/ontology/mappings/mondo_broadmatch_icd10cm.sssom.tsv -O $@

$(TMP_DIR)/ncit_icd10_2017.sssom.tsv: | $(TMP_DIR)/
	wget https://raw.githubusercontent.com/mapping-commons/disease-mappings/main/mappings/ncit_icd10_2017.sssom.tsv -O $@


$(BOOMER_INPUT_DIR)/%/combined.sssom.tsv $(BOOMER_INPUT_DIR)/%/prefix.yaml: $(ALL_MAPPINGS) | $(BOOMER_INPUT_DIR)/%/
	python $(HOME_DIR)/scripts/gen_boomer_input.py run \
		--source-location $(TMP_DIR) \
		--target-location $(BOOMER_INPUT_DIR)/$* \
		--config ../mondo-icd10cm.symbiont.yaml

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
		--window-count 100 \
		--runs 10 \
		--restrict-output-to-prefixes=MONDO \
		--restrict-output-to-prefixes=ICD10CM
	find $(BOOMER_OUTPUT_DIR)/no_mappings -name "*.json" -type 'f' -size -500c -delete # Hack for removing individual singleton json files.

boomer-exact_match_only: | $(BOOMER_OUTPUT_DIR)/exact_match_only/
	boomer --ptable $(BOOMER_INPUT_DIR)/exact_match_only/combined.ptable.tsv \
		--ontology $(BOOMER_INPUT_DIR)/exact_match_only/symbiont-merged-all.owl \
		--prefixes $(BOOMER_INPUT_DIR)/exact_match_only/prefix.yaml \
		--output $(BOOMER_OUTPUT_DIR)/exact_match_only/boomer_output \
		--window-count 10 \
		--runs 1 \
		--restrict-output-to-prefixes=MONDO \
		--restrict-output-to-prefixes=ICD10CM
	find $(BOOMER_OUTPUT_DIR)/exact_match_only -name "*.json" -type 'f' -size -500c -delete # Hack for removing individual singleton json files.

boomer-all_precise: | $(BOOMER_OUTPUT_DIR)/all_precise/
	boomer --ptable $(BOOMER_INPUT_DIR)/all_precise/combined.ptable.tsv \
		--ontology $(BOOMER_INPUT_DIR)/all_precise/symbiont-merged-all.owl \
		--prefixes $(BOOMER_INPUT_DIR)/all_precise/prefix.yaml \
		--output $(BOOMER_OUTPUT_DIR)/all_precise/boomer_output \
		--window-count 10 \
		--runs 1 \
		--restrict-output-to-prefixes=MONDO \
		--restrict-output-to-prefixes=ICD10CM
	find $(BOOMER_OUTPUT_DIR)/all_precise -name "*.json" -type 'f' -size -500c -delete # Hack for removing individual singleton json files.

boomer-all: | $(BOOMER_OUTPUT_DIR)/all/
	boomer --ptable $(BOOMER_INPUT_DIR)/all/combined.ptable.tsv \
		--ontology $(BOOMER_INPUT_DIR)/all/symbiont-merged-all.owl \
		--prefixes $(BOOMER_INPUT_DIR)/all/prefix.yaml \
		--output $(BOOMER_OUTPUT_DIR)/all/boomer_output \
		--window-count 10 \
		--runs 1 \
		--restrict-output-to-prefixes=MONDO \
		--restrict-output-to-prefixes=ICD10CM
	find $(BOOMER_OUTPUT_DIR)/all -name "*.json" -type 'f' -size -500c -delete # Hack for removing individual singleton json files.


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

JSONS_EXACT_MATCH_ONLY=$(wildcard $(BOOMER_OUTPUT_DIR)/exact_match_only/boomer_output/*.json)
PNGS_EXACT_MATCH_ONLY=$(patsubst %.json, %.png, $(filter-out singletons, $(JSONS_EXACT_MATCH_ONLY)))

.PHONY: reports-exact_match_only
reports-exact_match_only: $(PNGS_EXACT_MATCH_ONLY)

JSONS_ALL_PRECISE=$(wildcard $(BOOMER_OUTPUT_DIR)/all_precise/boomer_output/*.json)
PNGS_ALL_PRECISE=$(patsubst %.json, %.png, $(filter-out singletons, $(JSONS_ALL_PRECISE)))

.PHONY: reports-all_precise
reports-all_precise: $(PNGS_ALL_PRECISE)

JSONS_ALL=$(wildcard $(BOOMER_OUTPUT_DIR)/all/boomer_output/*.json)
PNGS_ALL=$(patsubst %.json, %.png, $(filter-out singletons, $(JSONS_ALL)))

.PHONY: reports-all
reports-all: $(PNGS_ALL)


include custom.Makefile