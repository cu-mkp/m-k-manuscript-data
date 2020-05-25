CHANGED_FILES=

if [ "${TRAVIS_PULL_REQUEST}" = "false" ] ; then
    # This isn't a PR build.
    COMMIT_RANGE="$(echo ${TRAVIS_COMMIT_RANGE} | cut -d '.' -f 1,4 --output-delimiter '..')"
    CHANGED_FILES="$(git diff --name-only ${COMMIT_RANGE} --)"
else
    # This is a PR build.
    CHANGED_FILES="$(git diff --name-only ${TRAVIS_BRANCH}..HEAD --)"
    python check_update.py
fi
echo "End Test"