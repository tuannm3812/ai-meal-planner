# UTS poster blocks

Native poster blocks and styles for the deck-kit poster engine, following [the poster template](../POSTER-TEMPLATE.md).
Reference build: the Synogize harness poster (`project-15-strategy/deliverables/portfolio-showcase/uts-deck/poster/`).

In a poster spec:

```json
{"plugin": "<kit>/templates/poster/uts_poster_blocks.py", "css": "<kit>/templates/poster/uts_poster.css"}
```

Use `uts_poster_landscape.css` for landscape. Each block's fields are listed at the top of `uts_poster_blocks.py`.
Verified 17 November 2026 by rendering the Synogize portrait and landscape posters from these copies (no problems,
text identical to the project build).

## AI Meal Planner poster (A1 portrait and landscape)

`meal-poster.json` is the portrait spec and `meal-poster-landscape.json` the landscape one (three column stacks), `meal_poster_blocks.py` adds this poster's blocks on top of `uts_poster_blocks.py`
(plates, kitchen stations, app steps, two-part donuts, Viridis result bars, the hard-limits funnel, architecture,
limits as insights, a QR card), and `meal_poster.css` holds every style the poster uses. `logo-lockup.svg` puts the
AI Meal Planner mark beside the unaltered UTS logo at one height (`build_logo_lockup.py` rebuilds it).

Render (needs the deck-kit checkout and its `.venv`, plus poppler):

```bash
docs/showcase/uts-deck/poster/render_meal_poster.sh
```

It writes `../output/poster.pdf` (594 × 841 mm) and `poster-landscape.pdf` (841 × 594 mm), each with a PNG 6000 px on
its long side; pass `portrait` or `landscape` to render one. Blocks take `vars` (CSS variables such as column counts) so
one stylesheet serves both. The engine fails on any
block that overflows, any type size outside the seven levels, or a number missing from `../claims-register.md`.
Numbers come from that register: 0.5% median calorie gap, 152 of 152 offline and 144 of 152 on USDA, 72 of 72 on
pinned USDA foods (PR #61), 143 of 144 on workout days (PR #57), 662 tests at 97% coverage.
