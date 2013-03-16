#!/bin/sh

cd $(dirname "$0")
./win.sh ./test.sh
RC=$?
if [ "${RC}" != "0" ]; then
    echo "Tests failed, aborting."
    exit ${RC}
fi

RAW_VERSION=$(python setup.py --version)
# Remove whitespace from ${RAW_VERSION}
VERSION=${RAW_VERSION//[[:space:]]/}
TAG="v${VERSION}"

git tag ${TAG} && \
python setup.py sdist upload && \
python -c "import setuptools; execfile('setup.py')" bdist_egg upload && \
git push origin ${TAG}
