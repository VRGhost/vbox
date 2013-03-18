#!/bin/sh
#
# Please note that this script assumes that caller has setuptools and docutils installed.
cd $(dirname "$0")

function fail_with_rc {
    MSG=$1
    RC=$2
    if [ "${RC}" = "0" ]; then
        RC=1
    fi
    echo -e "\n\n===============" 1>&2
    echo ${MSG} 1>&2
    echo "Aborting." 1>&2
    exit ${RC}
}

function fail_on_nz_rc {
    RC=$?
    MSG=$1
    if [ "${RC}" != "0" ]; then
        fail_with_rc "${MSG}" "${RC}"
    fi
}

if [ -n "$(git status --porcelain 2>/dev/null | grep '^[[:space:]]*M[[:space:]]')" ]; then
    git status
    fail_with_rc "There are uncommited changes." "1"
fi
ecit 42

RST2HTML_ERR="./rst2html_err.tmp"
{ python setup.py --long-description | python rst2html.py > /dev/null ; } 2>&1 | tee ${RST2HTML_ERR}
ERR_MSG=$(cat "${RST2HTML_ERR}" )
rm "${RST2HTML_ERR}"

RC=$?
if [ \( "${RC}" != "0" \) -o \( -n "${ERR_MSG}" \) ]; then
    fail_with_rc "Rst2Html check failed." "${RC}"
fi

python setup.py register
fail_on_nz_rc "PyPy login failed."

./test
fail_on_nz_rc "Tests failed."

RAW_VERSION=$(python setup.py --version)
# Remove whitespace from ${RAW_VERSION}
VERSION=${RAW_VERSION//[[:space:]]/}
TAG="v${VERSION}"

SRC_BRANCH=$(git branch | grep '^*' | cut -f 2 -d ' ')
TRG_BRANCH="release"

git checkout "${TRG_BRANCH}" && \
git merge "${SRC_BRANCH}" --squash --message "Releasing ${TAG}."
fail_on_nz_rc "Git merge failed."

git tag ${TAG} && \
git push origin ${TAG} && \
git push
fail_on_nz_rc "Git push failed."

python setup.py sdist upload && \
python -c "import setuptools; execfile('setup.py')" bdist_egg upload && \
fail_on_nz_rc "Python upload failed."

# Revert to original source branch
git checkout "${SRC_BRANCH}"