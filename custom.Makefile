########################################
## Custom extension to automatically  ##
## generated Mapping Commons Makefile ##

ROBOT=robot

MONDO_ICD10CM_BOOMER=projects/mondo-icd10cm/boomer_output/no_mappings/no_mappings.ofn

$(TMP_DIR)/mondo_icd10cm_boomer.json: $(MONDO_ICD10CM_BOOMER) | $(TMP_DIR)/
	$(ROBOT) convert -i $< -f json -o $@

$(MAPPINGS_DIR)/mondo_icd10cm_boomer.sssom.tsv: $(TMP_DIR)/mondo_icd10cm_boomer.json
	sssom convert $< -o $@
