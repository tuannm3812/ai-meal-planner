# AI Meal Planner deck on the UTS deck kit

Audience and presentation setting: portfolio readers (hiring managers, lecturers) reading without a presenter; also a 10-minute talk.

Purpose and reader question: what the planner does, how it works, what was measured and what is unproven.

Evidence cutoff: `main` at a4fc80b, 7 November 2026 (benchmark rerun after PRs #43 and #45). Claims are in claims-register.md.

Kit version and exact commit: see kit-pin.json (0.6.0). Identity is none: this is a personal project, not UTS coursework.

Chapter accents (structure only): Overview slate, How it works blue, Evidence plum, Limits and next steps ochre.

Summary themes: Sized to you slate, On target blue, Fits your limits plum, Honest about gaps ochre.

Data colours (Viridis, one meaning each): body and activity #3B528B, model exercise #21918C; estimated #440154, reference #21918C; protein #3B528B, carbs #21918C, fat #5EC962; counts and plan bars #3B528B; running today #21918C, waiting grey #89949D. Estimated and Reference are also written in words.

Assets: plate illustrations are the project's own flat artwork (docs/showcase/slides/build_cover_art.py); app captures are real React screens from a local run, 6 November 2026.

Glossary: plan, meal target (28% of the daily budget, 350–850 kcal), daily budget, benchmark (72 offline requests), wider check (68 by-name requests), fallback meal, estimated, reference.

Layouts: cover, agenda and close are the kit's own; slides 3–15 use project layouts in project_layouts.py (mp_*), with neutral cards, chapter-accent rules, and wording only from slide fields.

Review log: 18 November 2026, batch 1 ported on built-in layouts; then Mike asked for the whole deck, so slides 3–15 moved to project layouts. Build, export, check_deck, audit_layout and check_markers all report 0.

- 2026-11-19: cover uses a real CC0 photo of chicken fried rice (Andy Li, Wikimedia Commons; see `assets/photos/cover-chicken-fried-rice.provenance.json`). Tags pin to the real chicken, rice and carrot, and each leader meets its tag edge. Tag weights are the app's plan, not the photo's portions. Affiliation reads TD School, University of Technology Sydney.
- 2026-11-19 batch 1: slide 3 cards gain unit charts (gap band, 72 dots, 5 checks, 68 of 72 dots); slide 4 uses a real CC0 spaghetti bolognese photo (Andy Li) with numbered pins that match the three question rows, and its right-hand boxes now end inside the right rail.
- 2026-11-19 batch 2: slide 5 uses readable close-ups cropped from the same captures; slide 6 replaces each output chip with an order ticket that gains one line per station; slide 8 draws the funnel as one dot per recipe (outlined rings for removed recipes).
- 2026-11-19 slide 7: steps drawn as four SVG chevrons (the renderer has only rectangles and ellipses, so shapes are images and all text stays native); the day and the meal as a two-ring donut (outer: meal 28% vs rest; inner: body and activity vs exercise).
- 2026-11-19 icon kit: every icon now comes from assets/icons/kit (build_icon_kit.py): Material Symbols Rounded on a white rounded tile with a thin edge, glyph in one of six tones (four chapter inks, teal, grey). 29 glyphs x 6 tones. Replaces the white-glyph-in-a-solid-circle icons.
- 2026-11-19 owner feedback: icons are bare Material glyphs (no tile), drawn a third larger; slide 7 chevrons wear the ring colours (blue body, teal exercise, dark budget, green meal) above two separate rings, each with one insight; explanatory captions (dot legends on slide 3, the slide 7 scale note, the slide 13 colour legend) moved to the speaker notes.
- 2026-11-19 batch 3: slide 10 gets the ±10% pass band with the worked example on it (macro caption moved to notes); slide 11 labels each fix's gain (+31, +6, +25) on a dashed step; slide 13 stat cards get a 538/92 split bar, a 95% bar with the 89% floor tick, and five check icons. Slide 12 kept.
- 2026-11-21 slide 12: rebuilt after the text-to-SQL full-flow slide: four stage lanes left to right (Ask, API, Plan, Answer), numbered steps 1 to 8 top to bottom inside each, exits from step 4 (fallback, refused) level with it, and a band of four guarantees. All native shapes and text. The build-stack bar moved out (deploy tools are on slide 13; Gemini is an optional note on step 8).
- 2026-11-21 batch 4: slide 14 drops its explanatory heading for strength dots (three, two, one) and a "closes it" step per card; slide 15 gets kit icons on every task; slide 16 closes on the cover's chicken fried rice photo (same CC0 source) with a one-line result caption.
- 2026-11-22 numbers refreshed against main after PRs #47 to #49 (benchmark, wider check, retriever funnel, "pasta" run and pytest all rerun on a clean export of main): 76 recipes; median gap 0.5%; 152 of 152 wider; funnel 76, 30, 6, 1; slide 4 pasta is now Tuna Pasta Salad ($14.70); 662 tests (570 + 92) at 97%; next steps moved the merged workout and allergen work to a 22 Nov milestone. Close uses a CC0 photo of two different bowls (Andy Li).
- 2026-11-23 appendix A5 and A6: the workout check (stacked budget bars with an outline for the usual week's exercise that is no longer added) and the USDA benchmark (offline, first run, kJ fixed, out of 72), both on project layout `mp_bench`. Slides 14, 15 and A1 updated to match.
