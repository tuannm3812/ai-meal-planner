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
