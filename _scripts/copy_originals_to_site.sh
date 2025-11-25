#!/usr/bin/env sh
# Copy photo originals into the built site directory.
# Safe and idempotent. Intended to be run after `quarto render` / build.

set -eu

SRC_DIR="_assets/images/photos"
DST_DIR="_site/_assets/images/photos"

found=0

if [ ! -d "$SRC_DIR" ]; then
  echo "Source directory $SRC_DIR not found; nothing to copy." >&2
  exit 0
fi

for d in "$SRC_DIR"/*; do
  if [ -d "$d/originals" ]; then
    slug=$(basename "$d")
    mkdir -p "$DST_DIR/$slug/originals"
    # Use cp -a when available; fall back to plain cp
    if command -v cp >/dev/null 2>&1; then
      cp -a "$d/originals/." "$DST_DIR/$slug/originals/" || true
    else
      # POSIX fallback
      for f in "$d/originals"/*; do
        [ -e "$f" ] || continue
        cp "$f" "$DST_DIR/$slug/originals/" || true
      done
    fi
    found=1
  fi
done

if [ "$found" -eq 0 ]; then
  echo "No originals found to copy." >&2
else
  echo "Copied originals into $DST_DIR"
fi

exit 0
