#!/usr/bin/env bash
set -euo pipefail
# Single entrypoint for _scripts: run bookmarks, projects, images, or all
DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_PY="$DIR/../.venv/bin/python"
PY="$VENV_PY"
if [ ! -x "$PY" ]; then
  if command -v python3 >/dev/null 2>&1; then PY=python3; else PY=python; fi
fi

cmd="${1:-help}"
shift || true

case "$cmd" in
  bookmarks)
    if [ -x "$DIR/gen-bookmarks.sh" ]; then
      "$DIR/gen-bookmarks.sh" "$@"
    else
      "$PY" "$DIR/generate-bookmarks.py" "$@"
    fi
    ;;

  projects)
    if [ -x "$DIR/gen-projects.sh" ]; then
      "$DIR/gen-projects.sh" "$@"
    else
      "$PY" "$DIR/generate-projects.py" "$@"
    fi
    ;;

  images)
    if [ -x "$DIR/download-bookmark-images.sh" ]; then
      "$DIR/download-bookmark-images.sh" "$@"
    else
      echo "download script not found: $DIR/download-bookmark-images.sh"
      exit 1
    fi
    ;;

  all)
    "$0" bookmarks "$@"
    "$0" projects "$@"
    ;;

  help|*)
    cat <<EOF
Usage: $0 {bookmarks|projects|images|all}

Examples:
  $0 bookmarks    # regenerate bookmarks/index.qmd
  $0 projects     # regenerate projects/index.qmd
  $0 images       # download bookmark images
  $0 all          # bookmarks + projects
EOF
    exit 1
    ;;
esac
