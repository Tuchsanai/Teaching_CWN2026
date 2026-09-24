#!/usr/bin/env bash
# Build the test image (same runtime + pytest) and run the suite with no network,
# so no test can reach a real model. The CLIs are replaced by tests/fake_bin/*.
set -euo pipefail
cd "$(dirname "$0")/.."
docker build -q --target test -t ai-chat-app:test . >/dev/null
docker run --rm --network none ai-chat-app:test python3 -m pytest -q -p no:cacheprovider /app/tests "$@"
