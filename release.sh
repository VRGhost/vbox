#!/bin/sh
cd $(dirname "$0")

RST2HTML_ERR="./rst2html_err.tmp"
{ python setup.py --long-description | python rst2html.py > /dev/null ; } 2>&1 | tee ${RST2HTML_ERR}
ERR_MSG=$(cat "${RST2HTML_ERR}" )
rm "${RST2HTML_ERR}"

RC=$?
if [ \( "${RC}" != "0" \) -o \( -n "${ERR_MSG}" \) ]; then
    echo "Rst2Html check failed. Aborting"
    exit ${RC}
fi

python setup.py register
RC=$?
if [ "${RC}" != "0" ]; then
    echo "PyPy login failed, aborting."
    exit ${RC}
fi

./test
RC=$?
if [ "${RC}" != "0" ]; then
    echo "Tests failed, aborting."
    exit ${RC}
fi

RAW_VERSION=$(python setup.py --version)
# Remove whitespace from ${RAW_VERSION}
VERSION=${RAW_VERSION//[[:space:]]/}
TAG="v${VERSION}"

python setup.py sdist upload && \
python -c "import setuptools; execfile('setup.py')" bdist_egg upload && \
git tag ${TAG} && \
git push origin ${TAG}
