PROJECT_DIR=projects
CONFIGDIR=config
MAKEFILE_TEMPLATE=$(CONFIGDIR)/Makefile.j2

ALL_PROJECTS=$(strip $(patsubst %.symbiont.yaml, %, $(notdir $(wildcard $(PROJECT_DIR)/*.yaml))))
ALL_SYMBIONT = $(patsubst %, symbiont-%, $(ALL_PROJECTS))

p:
	echo $(ALL_SYMBIONT)

all: $(ALL_SYMBIONT)

symbiont-%:
	mkdir -p $(PROJECT_DIR)/$*
	j2 $(MAKEFILE_TEMPLATE) $(PROJECT_DIR)/$*.symbiont.yaml > $(PROJECT_DIR)/$*/Makefile
	touch $(PROJECT_DIR)/$*/custom.Makefile
	cd $(PROJECT_DIR)/$* && make all
