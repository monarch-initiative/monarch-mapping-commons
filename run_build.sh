#!/usr/bin/env bash

set -e

MEMORY=${MEMORY:-20G}

IM=monarchinitiative/mapping-commons
VERSION=0.1.0

sh update_registry.sh
make -f docker.Makefile build

sh run.sh make IM=$IM MEMORY=$MEMORY mappings
sh run.sh make IM=$IM MEMORY=$MEMORY all
echo "The Mapping Commons run has been successfully completed."