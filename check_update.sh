if [ "${TRAVIS_PULL_REQUEST}" = "false" ] ; then
    # This isn't a PR build.
    true
else
    # This is a PR build.
    python check_update.py
fi