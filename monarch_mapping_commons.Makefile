
## Customize Makefile settings for monarch_mapping_commons
## 
## If you need to customize your Makefile, make
## changes here rather than in the main Makefile

RUN = poetry run

$(MAPPING_DIR)/mondo.sssom.tsv:
	mkdir -p $(MAPPING_DIR)
	wget http://purl.obolibrary.org/obo/mondo/mappings/mondo.sssom.tsv -O $@

$(MAPPING_DIR)/biomappings.sssom.tsv:
	mkdir -p $(MAPPING_DIR)
	mkdir -p tmp
	wget https://raw.githubusercontent.com/biopragmatics/biomappings/master/docs/_data/sssom/biomappings.sssom.tsv -O tmp/biomappings.sssom.tsv
	$(RUN) python3 scripts/process_biomappings.py --input tmp/biomappings.sssom.tsv --output $(MAPPING_DIR)/mesh_chebi_biomappings.sssom.tsv

$(MAPPING_DIR)/gene_mappings.sssom.tsv:
	mkdir -p $(MAPPING_DIR)
	wget http://data.monarchinitiative.org/monarch-gene-mapping/latest/gene_mappings.tsv -O $@
