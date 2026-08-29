#!/bin/sh
# No `set -e`: this container now stays alive for the whole submission
# (many test cases run against it via `docker exec`), so the entrypoint
# itself must not exit after the first command.

# Write the submission once, when the container starts, rather than once
# per test case.
echo "$SUBMISSION_CODE_B64" | base64 -d > /tmp/submission.py

# Keep the container alive so the host can `docker exec` into it for each
# test case. This is what actually removes the per-test-case overhead:
# `docker run` (full container create/start/network-namespace-setup/
# teardown) only happens once per submission now; each individual test
# only pays the much cheaper `docker exec` cost.
exec sleep infinity