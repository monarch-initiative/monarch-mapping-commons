#!/usr/bin/env bash

MAKEFILE_TEMPLATE=config/commons.Makefile.j2

j2 "$MAKEFILE_TEMPLATE" registry.yaml > Makefile

touch custom.Makefile