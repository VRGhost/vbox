#!/bin/sh

cd $(dirname "$0")
./win_test.sh
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
git push origin ${TAG}