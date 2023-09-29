
## Customize Makefile settings for monarch_mapping_commons
## 
## If you need to customize your Makefile, make
## changes here rather than in the main Makefile


$(MAPPING_DIR)/mondo.sssom.tsv:
	mkdir -p $(MAPPING_DIR)
	wget http://purl.obolibrary.org/obo/mondo/mappings/mondo.sssom.tsv -O $@

$(MAPPING_DIR)/biomappings.sssom.tsv:
	mkdir -p $(MAPPING_DIR)
	wget https://raw.githubusercontent.com/biopragmatics/biomappings/master/docs/_data/sssom/biomappings.sssom.tsv -O $@

$(MAPPING_DIR)/gene_mappings.sssom.tsv:
	mkdir -p $(MAPPING_DIR)
	wget http://data.monarchinitiative.org/monarch-gene-mapping/latest/gene_mappings.tsv -O $@
