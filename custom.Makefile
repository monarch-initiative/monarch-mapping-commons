######################################
# Custom extension to automatically  #
# generated Mapping Commons Makefile #
######################################

RUN = poetry run

.PHONY: install
install:
	poetry install

ROBOT=robot

MONDO_ICD10CM_BOOMER=projects/mondo-icd10cm/boomer_output/exact_match_only/boomer_output.ofn

$(TMP_DIR)/mondo_icd10cm_boomer.json: $(MONDO_ICD10CM_BOOMER) | $(TMP_DIR)/
	$(ROBOT) query -i $< --update sparql/equivalent_to_exactmatch.ru convert -o $@

$(MAPPINGS_DIR)/mondo_icd10cm_boomer.sssom.tsv: $(TMP_DIR)/mondo_icd10cm_boomer.json
	sssom parse $< --input-format obographs-json -m config/metadata.yaml --prefix-map-mode merged -o $@

MONDO_JSON=http://purl.obolibrary.org/obo/mondo/mondo.json

$(TMP_DIR)/mondo.json:
	wget $(MONDO_JSON) -O $@

$(MAPPINGS_DIR)/mondo_all.sssom.tsv: $(TMP_DIR)/mondo.json
	sssom parse $< --input-format obographs-json -m config/metadata.yaml --prefix-map-mode merged -o $@

.PHONY: biomappings
biomappings: install
	$(RUN) python3 scripts/biomappings.py $(MAPPINGS_DIR)/biomappings.sssom.tsv
