#!/usr/bin/env bash
set -euo pipefail
# Download featured images for projects into _assets/images/projects/
DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$DIR/.." && pwd)"
ASSETS_DIR="$ROOT_DIR/_assets/images/projects"
mkdir -p "$ASSETS_DIR"

echo "Downloading featured project images into $ASSETS_DIR"

for proj in "$ROOT_DIR"/projects/*; do
  [ -d "$proj" ] || continue
  name=$(basename "$proj")
  file="$proj/index.qmd"
  if [ ! -f "$file" ]; then
    echo "  - Skipping $name (no index.qmd)"
    continue
  fi

  # Extract the first 'image:' frontmatter line
  url=$(grep -m1 '^image:' "$file" | sed -E 's/^image:[[:space:]]*//; s/^"//; s/"$//') || true
  if [ -z "$url" ]; then
    echo "  - No image for $name"
    continue
  fi

  # Strip query string to get extension
  url_nq="${url%%\?*}"
  ext="${url_nq##*.}"
  # sanitize extension
  if [[ ${#ext} -gt 5 || "$ext" == "$url_nq" ]]; then
    ext="jpg"
  fi

  target="$ASSETS_DIR/${name}.${ext}"
  if [ -f "$target" ]; then
    echo "  - Skipping $name (already downloaded) -> $(basename "$target")"
    continue
  fi

  echo "  - Downloading $name -> $(basename "$target")"
  if command -v curl >/dev/null 2>&1; then
    curl -sS -L --fail -o "$target" "$url"
  elif command -v wget >/dev/null 2>&1; then
    wget -q -O "$target" "$url"
  else
    echo "Neither curl nor wget available; cannot download $url" >&2
    exit 1
  fi

done

echo "Done. Images saved to $ASSETS_DIR"
