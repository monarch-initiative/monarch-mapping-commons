#!/bin/sh

# Wrapper script for docker.
#
# This is used primarily for wrapping the GNU Make workflow.
# Instead of typing "make TARGET", type "./run.sh make TARGET".
# This will run the make workflow within a docker container.
#
# Assumes that you are working in the root directory


IMAGE=${IMAGE:-monarchinitiative/mapping-commons}
MEMORY=${MEMORY:-20G}

ODK_DEBUG=${ODK_DEBUG:-no}

TIMECMD=
if [ x$ODK_DEBUG = xyes ]; then
    # If you wish to change the format string, take care of using
    # non-breaking spaces (U+00A0) instead of normal spaces, to
    # prevent the shell from tokenizing the format string.
    TIMECMD="/usr/bin/time -f ### DEBUG STATS ###\nElapsed time: %E\nPeak memory: %M kb"
fi

echo "Running Process with Memory $MEMORY and Image $IMAGE"
docker run -v $PWD/:/work -w /work -e ROBOT_JAVA_ARGS="-Xmx${MEMORY}" -e JAVA_OPTS="-Xmx${MEMORY}" --rm -ti $IMAGE $TIMECMD "$@"
