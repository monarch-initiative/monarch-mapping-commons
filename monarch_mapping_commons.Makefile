
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


benchmark:
	pip install py-spy
	sudo py-spy record -o flamegraph.svg -- $(SSSOM_TOOLKIT) validate $(MAPPING_DIR)/gene_mappings.sssom.tsv


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
	if [ -z "${GH_ACTION}" ] || [ ${GH_ACTION} = false ]; then
		mkdir -p $(MAPPING_DIR) $(TMP_DIR)
		$(RUN) gene-mapping generate --download --preprocess-uniprot --output-dir $(TMP_DIR)
		$(RUN) sssom parse $(TMP_DIR)/gene_mappings.sssom.tsv -m $(METADATA_DIR)/gene_mappings.sssom.yml --prefix-map-mode merged -o $@
	else
		echo "Gene Mappings target is unavailable in GitHub actions."
	fi


$(MAPPING_DIR)/hp_mesh.sssom.tsv:
	wget https://raw.githubusercontent.com/monarch-initiative/umls-ingest/main/src/umls_ingest/mappings/hp_mesh.sssom.tsv -O $@


$(MAPPING_DIR)/umls_hp.sssom.tsv:
	wget https://raw.githubusercontent.com/monarch-initiative/umls-ingest/main/src/umls_ingest/mappings/umls_hp.sssom.tsv -O $@


$(TMP_DIR)/upheno/%:
	mkdir -p $(TMP_DIR)/upheno/
	wget https://bbop-ontologies.s3.amazonaws.com/upheno/current/upheno-release/all/$* -O $@


$(MAPPING_DIR)/upheno_custom.sssom.tsv: $(patsubst %, $(TMP_DIR)/upheno/%, upheno_species_lexical.csv upheno_mapping_logical.csv upheno_all_with_relations.owl)
	mkdir -p $(MAPPING_DIR) $(TMP_DIR)
	phenio-toolkit lexical-mapping --species-lexical $(TMP_DIR)/upheno/upheno_species_lexical.csv -m $(TMP_DIR)/upheno/upheno_mapping_logical.csv -o $(TMP_DIR)
	sssom parse $(TMP_DIR)/upheno_custom_mapping.sssom.tsv --metadata $(METADATA_DIR)/upheno_custom_mapping.sssom.yml -C merged -o $@
