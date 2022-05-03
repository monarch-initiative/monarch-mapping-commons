#!/usr/bin/env bash

set -e

IM=monarchinitiative/mapping-commons

docker run -e ROBOT_JAVA_ARGS='-Xmx56G' \
  -e JAVA_OPTS='-Xmx56G' \
  -v $PWD/:/work \
  -w /work --rm -ti $IM "$@"
