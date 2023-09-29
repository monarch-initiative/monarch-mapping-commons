
## Customize Makefile settings for monarch_mapping_commons
## 
## If you need to customize your Makefile, make
## changes here rather than in the main Makefile

MAPPING_DIR = 					mappings
SCRIPT_DIR =					scripts
SRC_DIR = 						sources
TMP_DIR = 						tmp
RUN = poetry run


$(MAPPING_DIR)/ $(SCRIPT_DIR)/ $(SRC_DIR)/ $(TMP_DIR)/:
	mkdir -p $@

$(MAPPING_DIR)/mondo.sssom.tsv: | $(MAPPING_DIR)/
	wget http://purl.obolibrary.org/obo/mondo/mappings/mondo.sssom.tsv -O $@

$(MAPPING_DIR)/biomappings.sssom.tsv: | $(MAPPING_DIR)/ $(SCRIPT_DIR)/ $(TMP_DIR)/
	wget https://raw.githubusercontent.com/biopragmatics/biomappings/master/docs/_data/sssom/biomappings.sssom.tsv -O $(TMP_DIR)/biomappings.sssom.tsv
	$(RUN) python3 $(SCRIPT_DIR)/process_biomappings.py --input $(TMP_DIR)/biomappings.sssom.tsv --output $(MAPPING_DIR)/mesh_chebi_biomappings.sssom.tsv

$(MAPPING_DIR)/gene_mappings.sssom.tsv:
	wget http://data.monarchinitiative.org/monarch-gene-mapping/latest/gene_mappings.tsv -O $@
