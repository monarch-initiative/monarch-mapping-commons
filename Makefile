###Configuration
#
# These are standard options to make Make sane:
# <http://clarkgrubb.com/makefile-style-guide#toc2>

MAKEFLAGS += --warn-undefined-variables
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := all
.DELETE_ON_ERROR:
.SUFFIXES:
.SECONDARY:

VERSION_MAKEFILE = 				0.1
TODAY ?=                    	$(shell date +%Y-%m-%d)
ROBOT =							robot
MAPPING_DIR = 					mappings
SCRIPT_DIR =					scripts
SRC_DIR = 						sources
TMP_DIR = 						tmp
SSSOM_TOOLKIT = 				sssom
TSVALID = 						tsvalid


$(MAPPING_DIR)/ $(SCRIPT_DIR)/ $(SRC_DIR)/ $(TMP_DIR)/:
	mkdir -p $@

#######################################
##### Mapping maintenance  ############
#######################################

mapping-%:
	make $(MAPPING_DIR)/$*.sssom.tsv -B

.PHONY: mappings
mappings:
	make $(shell grep local_name registry.yml | sed 's/local_name: /$(MAPPING_DIR)\//' )

#######################################
##### Mapping validation  #############
#######################################

validate-%:
	tsvalid $(MAPPING_DIR)/$*.sssom.tsv --comment "#"
	$(SSSOM_TOOLKIT) validate $(MAPPING_DIR)/$*.sssom.tsv
	$(SSSOM_TOOLKIT) convert $(MAPPING_DIR)/$*.sssom.tsv --output-format rdf -o $(TMP_DIR)/$*.sssom.ttl

MAPPINGS=$(notdir $(wildcard $(MAPPING_DIR)/*.sssom.tsv))
VALIDATE_MAPPINGS=$(patsubst %.sssom.tsv, validate-%, $(MAPPINGS))

.PHONY: validate-mappings
validate-mappings: 
ifeq ($(strip $(MAPPINGS)),)	# Check if MAPPINGS is empty
	@echo "No mappings found to validate."
else
	$(MAKE) $(VALIDATE_MAPPINGS)
endif

#######################################
##### Mappings  #######################
#######################################

$(MAPPING_DIR)/%.sssom.tsv:
	echo "The $* command is not currently implemented"

#######################################
##### Utilities  ######################
#######################################

.PHONY: test
test: validate-mappings

.PHONY: version
version:
	@echo "Mapping Commons Makefile version: $(VERSION_MAKEFILE) (this is the version of the Mapping Commons Toolkit with which this Makefile was generated)" &&\
	$(ROBOT) --version

# Install cruft if not already installed (needed for running in ODK).
.PHONY: install-cruft
install-cruft: 
	@if ! which cruft > /dev/null; then \
		echo "Installing cruft..."; \
		pip install cruft; \
	else \
		echo "cruft is already installed."; \
	fi

# Check we are up-to-date with the template
.PHONY: cruft-check
cruft-check: install-cruft
	cruft check

# To view any differences from the template
.PHONY: cruft-diff
cruft-diff: install-cruft
	cruft diff

# To update to the latest version of the template
.PHONY: update-repo
update-repo: install-cruft
	cruft update

# To update a project to use new values of template variables
.PHONY: update-variables
update-variables: config/project-cruft.json install-cruft
	cruft update --variables-to-update-file $<

.PHONY: public-release
public-release:
	echo "The $* command is not currently implemented" && fail

.PHONY: clean
clean:
	[ -n "$(TMP_DIR)" ] && [ $(TMP_DIR) != "." ] && [ $(TMP_DIR) != "/" ] && [ $(TMP_DIR) != ".." ] && [ -d ./$(TMP_DIR) ] && rm -rf ./$(TMP_DIR)/*

.PHONY: help
help:
	@echo "$$data"

define data
Usage: [IMAGE=(odklite|odkfull)] [ODK_DEBUG=yes] sh odk.sh make command

----------------------------------------
	Command reference
----------------------------------------

Core commands:
* mappings:				Rebuild all mapping files
* test:					Run all validation tests
* version:				Show the current version of the Mapping Commons Makefile and ROBOT.
* help:					Print Mapping Commons Usage information
* public-release:			Uploads the release file to a release management system, such as GitHub releases. Must be configured.

Mapping management:
* mapping-%:				Updates the mapping with the id %.
* validate-%:				Validates the mapping with the id %.

Repo management:
* update-repo:				Update the repository to the latest version of the template.
* update-variables:			Update the repository to use new values for the template variables.
* cruft-check:				Check if the repository is up-to-date with the template.
* cruft-diff:				View any differences from the template.
* clean:				Delete all temporary files

Examples: 
* sh odk.sh make mappings
* sh odk.sh make update-repo
* sh odk.sh make test

Tricks:
* Add -B to the end of your command to force re-running it even if nothing has changed
* Use the IMAGE parameter to the odk.sh script to use a different image like odklite
* Use ODK_DEBUG=yes sh odk.sh make ... to print information about timing and debugging

endef
export data

include monarch_mapping_commons.Makefile