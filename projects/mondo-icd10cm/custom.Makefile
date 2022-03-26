
$(TMP_DIR)/icd10cm.ttl: | $(TMP_DIR)/
	wget https://data.bioontology.org/ontologies/ICD10CM/submissions/21/download?apikey=8b5b7825-538d-40e0-9e9e-5ab9274a9aeb -O $@

$(TMP_DIR)/icd10cm.owl: $(TMP_DIR)/icd10cm.ttl
	robot convert --input $< --format ttl --output $@
