#!/usr/bin/env bash
set -euo pipefail
# Wrapper to run generate-projects.py using the repo virtualenv when present
DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_PY="$DIR/../.venv/bin/python"
PY="$VENV_PY"
if [ ! -x "$PY" ]; then
  if command -v python3 >/dev/null 2>&1; then PY=python3; else PY=python; fi
fi

"$PY" "$DIR/generate-projects.py" "$@"
