#!/usr/bin/env bash
set -euo pipefail

find . -type f -name 'report.md' -print0 | while IFS= read -r -d '' file; do
  echo "Formatting: $file"

  tmp_header="$(mktemp)"
  tmp_body="$(mktemp)"
  tmp_formatted="$(mktemp)"
  tmp_final="$(mktemp)"

  # Save first 3 lines exactly as-is
  sed -n '1,3p' "$file" > "$tmp_header"

  # Save everything after line 3
  tail -n +4 "$file" > "$tmp_body" || true

  # Format only the body
  if [[ -s "$tmp_body" ]]; then
    mdformat --wrap 109 - < "$tmp_body" > "$tmp_formatted"
    cat "$tmp_header" "$tmp_formatted" > "$tmp_final"
  else
    # File has only 3 lines or fewer
    cat "$tmp_header" > "$tmp_final"
  fi

  mv "$tmp_final" "$file"
  rm -f "$tmp_header" "$tmp_body" "$tmp_formatted"
done