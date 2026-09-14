#!/usr/bin/env bash
set -u
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${PYTHON:-/opt/venv/bin/python3}"
if [[ ! -x "$PYTHON" ]]; then PYTHON=python3; fi
export PYTHONDONTWRITEBYTECODE=1
status=0
"$PYTHON" -B "$HERE/test_slides.py" --out-dir "$HERE" || status=1
"$PYTHON" -B "$HERE/test_ui.py" --out-dir "$HERE" || status=1
"$PYTHON" -B "$HERE/check_links.py" || status=1
exit "$status"
