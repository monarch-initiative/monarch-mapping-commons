# Need on path: boomer, robot

OWLS=ncit ordo doid mondo
TTLS=icd10cm
MAPS= ncit ordo doid mondo_hasdbref_icd10cm ncit_icd10_2016 ncit_icd10_2017
GET_OWLS=$(patsubst %, data/input/%.owl, $(OWLS))
GET_TTLS=$(patsubst %, data/tmp/%.ttl, $(TTLS))
GET_MAPPINGS=$(patsubst %, data/input/%.sssom.tsv, $(MAPS))
GET_PTABLES=$(patsubst %, data/input/%.ptable.tsv, $(MAPS))

all: get-onts get-mappings add-confidence

get-onts: $(GET_OWLS) $(GET_TTLS) data/input/icd10cm.owl
get-mappings: $(GET_MAPPINGS) | sssom
get-ptables: $(GET_PTABLES)


data/tmp/icd10cm.ttl: | data/tmp/
	wget https://data.bioontology.org/ontologies/ICD10CM/submissions/21/download?apikey=8b5b7825-538d-40e0-9e9e-5ab9274a9aeb -O $@

data/input/%.owl: | data/input/
	wget http://purl.obolibrary.org/obo/$*.owl -O $@

data/input/icd10cm.owl: data/tmp/icd10cm.ttl | data/tmp/
	robot convert --input $< --format ttl --output $@

data/input/%.sssom.tsv: data/input/
	wget https://raw.githubusercontent.com/mapping-commons/disease-mappings/new_mappings/mappings/$*.sssom.tsv -O $@

add-confidence:
	python -m scripts.add_confidence

data/output/%.ptable.tsv: data/input/confident_%.sssom.tsv
	sssom ptable $< -o $@

# data/output/combo.owl: data/input/
# 	robot merge -i $<doid.owl -i $<icd10cm.owl -i $<mondo.owl -i $<ncit.owl -i $<ordo.owl --output $@
data/output/combo.owl: data/input/*.owl
	robot merge $(addprefix -i, $^) --output $@

.PHONY: sssom
sssom:
	echo "skipping.."
#	python3 -m pip install --upgrade pip setuptools && python3 -m pip install --upgrade --force-reinstall git+https://github.com/mapping-commons/sssom-py.git@curie_detection_patch
#	python3 -m pip install --upgrade pip setuptools && python3 -m pip install --upgrade --force-reinstall sssom==0.3.7

dirs: data/ data/input/ data/tmp/ data/output
data/input/ data/tmp/ data/output/:
	mkdir -p $@

.PHONY: clean
clean: data
	rm -rf $<