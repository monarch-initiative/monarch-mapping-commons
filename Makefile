# Need on path: boomer, robot
DATA = data
INPUT = data/input
OUTPUT = data/output
TMP = data/tmp

# OWLS=ncit ordo doid mondo
ONTOLOGIES= mondo icd10cm
ONTOLOGY_PREFIXES= MONDO ICD10CM #In the final solution REMOVE ICD10 
BOOMER_INPUT=icd10cm  mondo
# MAPS= ncit ordo doid mondo_hasdbref_icd10cm ncit_icd10_2016 ncit_icd10_2017 mondo_exactmatch_icd10cm
MAPS = mondo_exactmatch_icd10cm
GET_OWLS=$(patsubst %, $(TMP)/%.owl, $(ONTOLOGIES))
GET_MAPPINGS=$(patsubst %, $(INPUT)/%.sssom.tsv, $(MAPS))
BOOMER_INPUT_FILES=$(patsubst %, $(TMP)/%.owl, $(BOOMER_INPUT))

all: get-onts get-mappings gen-boomer-input\
	 $(OUTPUT)/combo.owl \
	 $(OUTPUT)/combined_ptable.tsv \
	 boomer pngs

get-onts: $(GET_OWLS)
get-mappings: $(GET_MAPPINGS) | sssom

# data/output/combo.owl: data/input/
# 	robot merge -i $<doid.owl -i $<icd10cm.owl -i $<mondo.owl -i $<ncit.owl -i $<ordo.owl --output $@
$(OUTPUT)/combo.owl: $(GET_OWLS)
	robot merge $(addprefix -i , $^) --output $@

$(TMP)/%.owl: | $(INPUT)/
	wget http://purl.obolibrary.org/obo/$*.owl -O $@

$(TMP)/icd10cm.ttl: | $(TMP)/
	wget https://data.bioontology.org/ontologies/ICD10CM/submissions/21/download?apikey=8b5b7825-538d-40e0-9e9e-5ab9274a9aeb -O $@

$(TMP)/icd10cm.owl: $(TMP)/icd10cm.ttl | $(TMP)/
	robot convert --input $< --format ttl --output $@

$(INPUT)/mondo_hasdbref_icd10cm.sssom.tsv: $(INPUT)/
	wget https://raw.githubusercontent.com/monarch-initiative/mondo/master/src/ontology/mappings/mondo_hasdbxref_icd10cm.sssom.tsv -O $@

$(INPUT)/mondo_exactmatch_icd10cm.sssom.tsv: $(INPUT)/
	wget https://raw.githubusercontent.com/monarch-initiative/mondo/45f95c89d96d38db3d10b69cbb88a514afe01bff/src/ontology/mappings/mondo_exactmatch_icd10cm.sssom.tsv -O $@
$(INPUT)/%.sssom.tsv: $(INPUT)/
	wget https://raw.githubusercontent.com/mapping-commons/disease-mappings/main/mappings/$*.sssom.tsv -O $@

gen-boomer-input:
	python -m scripts.gen_boomer_input


$(OUTPUT)/combined_ptable.tsv: $(INPUT)/combined_sssom.tsv
	sssom ptable $< -o $@

boomer:
	boomer --ptable $(OUTPUT)/combined_ptable.tsv\
		   --ontology $(OUTPUT)/combo.owl \
		   --prefixes $(OUTPUT)/prefix.yaml \
		   --output $(OUTPUT)/boomer_output \
		   --window-count 10 \
		   --runs 100 
		#    $(addprefix --restrict-output-to-prefixes=, $(ONTOLOGY_PREFIXES))

	find $(OUTPUT)/boomer_output -name "*.json" -type 'f' -size -500c -delete

.PHONY: sssom
sssom:
	echo "skipping.."
#	python3 -m pip install --upgrade pip setuptools && python3 -m pip install --upgrade --force-reinstall git+https://github.com/mapping-commons/sssom-py.git@curie_detection_patch
#	python3 -m pip install --upgrade pip setuptools && python3 -m pip install --upgrade --force-reinstall sssom==0.3.7

dirs: data/ $(INPUT)/ $(TMP)/ $(OUTPUT) $(OUTPUT)/boomer_output
$(INPUT)/ $(TMP)/ $(OUTPUT)/ $(OUTPUT)/boomer_output:
	mkdir -p $@

.PHONY: clean
clean: data
	rm -rf $<

EXCLUDE_JSON= singletons.json
JSONS=$(wildcard $(OUTPUT)/boomer_output/*.json)
PNGS=$(patsubst %.json, %.png, $(JSONS))

$(OUTPUT)/boomer_output/%.json: $(OUTPUT)/boomer_output

%.dot: %.json
	og2dot.js -s boomer-style.json $< >$@ 
%.png: %.dot
	dot $< -Tpng -Grankdir=BT >$@

pngs: $(PNGS) 