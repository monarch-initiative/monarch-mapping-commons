
## Customize Makefile settings for monarch_mapping_commons
## 
## If you need to customize your Makefile, make
## changes here rather than in the main Makefile

MAPPING_DIR = 					mappings
SCRIPT_DIR =					scripts
SRC_DIR = 						sources
TMP_DIR = 						tmp
METADATA_DIR = 					metadata
RUN = poetry run


$(MAPPING_DIR)/ $(SCRIPT_DIR)/ $(SRC_DIR)/ $(TMP_DIR)/:
	mkdir -p $@

$(MAPPING_DIR)/mondo.sssom.tsv:
	mkdir -p $(MAPPING_DIR) $(TMP_DIR)
	wget http://purl.obolibrary.org/obo/mondo/mappings/mondo.sssom.tsv -O $@

$(MAPPING_DIR)/mesh_chebi_biomappings.sssom.tsv:
	mkdir -p $(MAPPING_DIR) $(TMP_DIR)
	wget https://raw.githubusercontent.com/biopragmatics/biomappings/master/docs/_data/sssom/biomappings.sssom.tsv -O $(TMP_DIR)/biomappings.sssom.tsv
	$(RUN) python3 $(SCRIPT_DIR)/process_biomappings.py --input $(TMP_DIR)/biomappings.sssom.tsv --output $(TMP_DIR)/mesh_chebi_biomappings.sssom.tsv
	$(RUN) sssom parse $(TMP_DIR)/mesh_chebi_biomappings.sssom.tsv -m $(METADATA_DIR)/mesh_chebi_biomappings.sssom.yml --prefix-map-mode merged -o $@

$(MAPPING_DIR)/gene_mappings.sssom.tsv:
	mkdir -p $(MAPPING_DIR) $(TMP_DIR)
	wget http://data.monarchinitiative.org/monarch-gene-mapping/latest/gene_mappings.sssom.tsv -O $(TMP_DIR)/gene_mappings.sssom.tsv
	$(RUN) sssom parse $(TMP_DIR)/gene_mappings.sssom.tsv -m $(METADATA_DIR)/gene_mappings.sssom.yml --prefix-map-mode merged -o $@


$(MAPPING_DIR)/hp_mesh.sssom.tsv:
	wget https://raw.githubusercontent.com/monarch-initiative/umls-ingest/main/src/umls_ingest/mappings/hp_mesh.sssom.tsv -O $@

$(MAPPING_DIR)/umls_hp.sssom.tsv:
	wget https://raw.githubusercontent.com/monarch-initiative/umls-ingest/main/src/umls_ingest/mappings/umls_hp.sssom.tsv -O $@

.PHONY: mappings_to_ttl
mappings_to_ttl: mappings
	$(RUN) python3 $(SCRIPT_DIR)/registry_parser.py registry.yml