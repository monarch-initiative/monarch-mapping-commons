
## Customize Makefile settings for monarch_mapping_commons
## 
## If you need to customize your Makefile, make
## changes here rather than in the main Makefile

all: mappings
mappings: $(ALL_MAPPINGS)

ALL_MAPPINGS = $(MAPPING_DIR)/mondo.sssom.tsv $(MAPPING_DIR)/biomappings.sssom.tsv $(MAPPING_DIR)/gene_mappings.tsv

$(MAPPINGS_DIR)/mondo.sssom.tsv: | $(MAPPINGS_DIR)/
	wget http://purl.obolibrary.org/obo/mondo/mappings/mondo.sssom.tsv -O $@

$(MAPPINGS_DIR)/biomappings.sssom.tsv: | $(MAPPINGS_DIR)/
	wget https://raw.githubusercontent.com/biopragmatics/biomappings/master/docs/_data/sssom/biomappings.sssom.tsv -O $@

$(MAPPINGS_DIR)/gene_mappings.tsv: | $(MAPPINGS_DIR)/
	wget http://data.monarchinitiative.org/monarch-gene-mapping/latest/gene_mappings.tsv -O $@
