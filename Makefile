# Need on path: boomer, robot
DATA = data
INPUT = data/input
OUTPUT = data/output

OWLS=ncit ordo doid mondo
TTLS=icd10cm
MAPS= ncit ordo doid mondo_hasdbref_icd10cm ncit_icd10_2016 ncit_icd10_2017
GET_OWLS=$(patsubst %, $(INPUT)/%.owl, $(OWLS))
GET_TTLS=$(patsubst %, data/tmp/%.ttl, $(TTLS))
GET_MAPPINGS=$(patsubst %, $(INPUT)/%.sssom.tsv, $(MAPS))


# GET_PTABLES=$(patsubst %, data/input/%.ptable.tsv, $(MAPS))

all: get-onts get-mappings gen-boomer-input $(OUTPUT)/combo.owl ptable boomer

get-onts: $(GET_OWLS) $(GET_TTLS) $(INPUT)/icd10cm.owl
get-mappings: $(GET_MAPPINGS) | sssom
# get-ptables: $(GET_PTABLES)


data/tmp/icd10cm.ttl: | data/tmp/
	wget https://data.bioontology.org/ontologies/ICD10CM/submissions/21/download?apikey=8b5b7825-538d-40e0-9e9e-5ab9274a9aeb -O $@

$(INPUT)/%.owl: | $(INPUT)/
	wget http://purl.obolibrary.org/obo/$*.owl -O $@

$(INPUT)/icd10cm.owl: data/tmp/icd10cm.ttl | data/tmp/
	robot convert --input $< --format ttl --output $@

$(INPUT)/%.sssom.tsv: $(INPUT)/
	wget https://raw.githubusercontent.com/mapping-commons/disease-mappings/new_mappings/mappings/$*.sssom.tsv -O $@

gen-boomer-input:
	python -m scripts.gen_boomer_input

# data/output/combo.owl: data/input/
# 	robot merge -i $<doid.owl -i $<icd10cm.owl -i $<mondo.owl -i $<ncit.owl -i $<ordo.owl --output $@
$(OUTPUT)/combo.owl: $(INPUT)/*.owl
	robot merge $(addprefix -i , $^) --output $@

.PHONY: ptable
ptable: $(INPUT)/combined_sssom.tsv
	sssom ptable $< -o $(OUTPUT)/combined_ptable.tsv

boomer:
	boomer --ptable $(OUTPUT)/combined_ptable.tsv\
		   --ontology $(OUTPUT)/combo.owl \
		   --prefixes $(OUTPUT)/prefix.yaml \
		   --output $(OUTPUT)/boomer_output \
		   --window-count 20 \
		   --runs 100 \
		   --restrict-output-to-prefixes=MONDO \
		   --restrict-output-to-prefixes=ICD10CM \
		   --restrict-output-to-prefixes=ICD10

	find $(OUTPUT)/boomer_output -name "*.json" -type 'f' -size -500c -delete

.PHONY: sssom
sssom:
	python3 -m pip install --upgrade pip setuptools && python3 -m pip install --upgrade --force-reinstall git+https://github.com/mapping-commons/sssom-py.git@curie_detection_patch
#	python3 -m pip install --upgrade pip setuptools && python3 -m pip install --upgrade --force-reinstall sssom==0.3.7

dirs: data/ $(INPUT)/ data/tmp/ $(OUTPUT) $(OUTPUT)/boomer_output
$(INPUT)/ data/tmp/ $(OUTPUT)/ $(OUTPUT)/boomer_output:
	mkdir -p $@

.PHONY: clean
clean: data
	rm -rf $<