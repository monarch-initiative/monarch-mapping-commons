#!/usr/bin/env bash

set -e

IM=monarchinitiative/mapping-commons
VERSION=0.1.0

sh update_registry.sh
docker build -t $IM:$VERSION . && docker tag $IM:$VERSION $IM:latest

sh run.sh make IM=$IM mappings
sh run.sh make IM=$IM all