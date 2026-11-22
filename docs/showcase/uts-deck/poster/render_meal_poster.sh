#!/usr/bin/env bash
# Render the AI Meal Planner poster: PDF and HTML via the deck-kit poster engine, then a 6000 px PNG.
# Set POSTER_HTML=path to keep the HTML. Needs the deck-kit checkout (DECK_KIT_ENGINE, default ~/Documents/GitHub/deck-kit) and its .venv, plus poppler.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ENGINE="${DECK_KIT_ENGINE:-$HOME/Documents/GitHub/deck-kit}"
OUT="$HERE/../output"
mkdir -p "$OUT"
cd "$ENGINE"
.venv/bin/python -m deck_kit.poster --project "$HERE/../deck-kit.json" --spec "$HERE/meal-poster.json" \
  --out "$OUT/poster.pdf" --html "${POSTER_HTML:-$(mktemp -d)/poster.html}" "$@"
# 6000 px on the long side (POSTER-TEMPLATE.md): A1 portrait is 841 mm tall, so 6000 / (841 / 25.4) dpi.
pdftoppm -png -singlefile -scale-to 6000 "$OUT/poster.pdf" "$OUT/poster"
echo "$OUT/poster.png"
