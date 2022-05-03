#!/usr/bin/env bash

set -e

IM=monarchinitiative/mapping-commons

docker run -e ROBOT_JAVA_ARGS='-Xmx48G' \
  -e JAVA_OPTS='-Xmx48G' \
  -v $PWD/:/work \
  -w /work --rm -ti $IM "$@"
