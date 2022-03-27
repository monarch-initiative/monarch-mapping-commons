########################################
## Custom extension to automatically  ##
## generated Mapping Commons Makefile ##

ROBOT=robot

MONDO_ICD10CM_BOOMER=projects/mondo-icd10cm/boomer_output/exact_match_only/boomer_output.ofn

$(TMP_DIR)/mondo_icd10cm_boomer.json: $(MONDO_ICD10CM_BOOMER) | $(TMP_DIR)/
	$(ROBOT) query -i $< --update sparql/equivalent_to_exactmatch.ru convert -o $@

$(MAPPINGS_DIR)/mondo_icd10cm_boomer.sssom.tsv: $(TMP_DIR)/mondo_icd10cm_boomer.json
	sssom parse $< --input-format obographs-json -m config/dummy.metadata.yaml -o $@
