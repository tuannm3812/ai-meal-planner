# Slide deck design history

Why rules changed. The current rules are in [DESIGN.md](DESIGN.md). Newest first.

## 6 November 2026

- **Strict slide standard adopted.** Mike asked for the discipline of his Project 15 and
  Text-to-SQL decks. Their grid, type roles, takeaway columns, markers, notes pattern and
  staged workflow carry over. Kitchen green, Bricolage Grotesque and Inter stay, because
  those are this product's approved identity. Replaced the slide row in the root `DESIGN.md`
  (30–32 pt titles, 14–18 pt body, 10-minute talk).
- **Charts drawn from shapes.** A native PowerPoint chart lost its category labels when
  converted to Google Slides, showing 1 to 4. Bars are now native shapes.
- **A 14-slide live deck replaced the first 12-slide one**, built to this standard while nobody had edited the first.
- **The live deck became the source of truth** once converted. `build_deck.js` is the seed.
- **Calorie claim corrected.** The first deck said the trained model predicts daily burn and
  sets the meal target. It predicts exercise calories. The claim rule is now in DESIGN.md.
