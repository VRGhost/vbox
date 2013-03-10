#!/bin/sh

export PY_27_ROOT=$(cygpath "C:\Python27_x64")
export VBOX_ROOT=$(cygpath "C:\Program Files\Oracle\VirtualBox")

export PATH="${VBOX_ROOT}":"${PY_27_ROOT}":${PATH}

$(dirname "$0")/test $*
