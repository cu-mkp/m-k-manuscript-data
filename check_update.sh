CHANGED_FILES=

if [ -z "${TRAVIS_COMMIT_RANGE}" ] ; then
    # This is a new branch.
    STATE = 'HERE'
else
    # This isn't a new branch.
    if [ "${TRAVIS_PULL_REQUEST}" = "false" ] ; then
        # This isn't a PR build.

        # We need the individual commits to detect force pushes.
        COMMIT1="$(echo ${TRAVIS_COMMIT_RANGE} | cut -f 1 -d '.')"
        COMMIT2="$(echo ${TRAVIS_COMMIT_RANGE} | cut -f 4 -d '.')"

        if [ "$(git cat-file -t ${COMMIT1} 2>/dev/null)" = commit -a "$(git cat-file -t ${COMMIT2} 2>/dev/null)" = commit ] ; then
            # This was a history rewrite.
        else
            # This is a 'normal' build.
            CHANGED_FILES="$(git diff --name-only ${COMMIT_RANGE} --)"
        fi
    else
        # This is a PR build.
        CHANGED_FILES="$(git diff --name-only ${TRAVIS_BRANCH}..HEAD --)"
    fi
fi