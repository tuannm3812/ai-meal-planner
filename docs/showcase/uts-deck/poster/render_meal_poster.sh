#!/usr/bin/env bash
# Render the AI Meal Planner poster, portrait and landscape, via the deck-kit poster engine:
# ../output/poster.pdf and poster-landscape.pdf, each with a PNG 6000 px on its long side (POSTER-TEMPLATE.md).
# Pass "portrait" or "landscape" to render one. Set POSTER_HTML_DIR to keep the HTML.
# Needs the deck-kit checkout (DECK_KIT_ENGINE, default ~/Documents/GitHub/deck-kit) and its .venv, plus poppler.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ENGINE="${DECK_KIT_ENGINE:-$HOME/Documents/GitHub/deck-kit}"
OUT="$HERE/../output"
HTML_DIR="${POSTER_HTML_DIR:-$(mktemp -d)}"
mkdir -p "$OUT" "$HTML_DIR"
status=0
for which in ${1:-portrait landscape}; do
  case "$which" in
    portrait) spec="meal-poster.json"; name="poster" ;;
    landscape) spec="meal-poster-landscape.json"; name="poster-landscape" ;;
    *) echo "unknown orientation: $which" >&2; exit 2 ;;
  esac
  echo "== $which"
  (cd "$ENGINE" && .venv/bin/python -m deck_kit.poster --project "$HERE/../deck-kit.json" --spec "$HERE/$spec" \
    --out "$OUT/$name.pdf" --html "$HTML_DIR/$name.html") || status=1
  pdftoppm -png -singlefile -scale-to 6000 "$OUT/$name.pdf" "$OUT/$name" 2>/dev/null
  echo "$OUT/$name.png"
done
exit $status
