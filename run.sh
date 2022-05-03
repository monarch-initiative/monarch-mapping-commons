#!/usr/bin/env bash

set -e

IM=monarchinitiative/mapping-commons

docker run -e ROBOT_JAVA_ARGS='-Xmx25G' \
  -e JAVA_OPTS='-Xmx25G' \
  -v $PWD/:/work \
  -w /work --rm -ti $IM "$@"
