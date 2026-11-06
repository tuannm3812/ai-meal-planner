# Showcase poster and slide deck

Everything for the project's showcase, laid out like the Text-to-SQL showcase folder.

## Editable deck

[Open the live Google Slides deck](https://docs.google.com/presentation/d/1KpI1000mDr8I143nNIUvZvncuwm51mZvPYzZvAm7hGM/edit),
in Drive at `06_Projects/AI Meal Planner`. Created 6 November 2026 with 14 editable slides.
Access is private; no sharing was changed.

**The live Google deck is the formatting source of truth.** Read its current objects before
editing, and don't overwrite it by rebuilding or importing the local PowerPoint.

- `build_deck.js` and `ai-meal-planner-deck.pptx`: the reviewed seed, historical from now on.
- [speaker-notes.md](speaker-notes.md): the deck's notes; keep aligned with the live deck.
- `ai-meal-planner-deck-google-slides.pdf`: export this at release (brief stage 6) and refresh
  it after later edits. It doesn't exist yet.

## How this folder works

Three questions, three kinds of file. Each has one owner, so nothing is decided twice.

| Question | File |
| --- | --- |
| What does each slide say? | [slides/BRIEF.md](slides/BRIEF.md) |
| How does every slide look? | [slides/DESIGN.md](slides/DESIGN.md) |
| How does the poster read and look? | [DESIGN.md](DESIGN.md) |
| Why did a rule change? | [slides/design-history.md](slides/design-history.md) |
| What may we quote? | [Fact sheet](#fact-sheet) below |
| What is the brand? | [root DESIGN.md](../../DESIGN.md) |
| What is the demo's provenance? | `slides/captures/`: screens plus a `.json` record |

| Folder or file | Holds |
| --- | --- |
| `slides/` | Brief, standard, history, `assets/` (mark, QR), `captures/`, `capture_app.py`, `cover-concepts/`, `palette-trials/` |
| `fonts/` | Bundled Google Sans and Google Sans Code (showcase), Bricolage Grotesque and Inter (current drafts), with OFL licences |
| `poster.html`, `linkedin.html`, `showcase.css`, `render.py` | Poster and LinkedIn source and renderer |
| `ai-meal-planner-*.png`, `.pdf`, `linkedin_post.md` | First poster outputs and post text |

**For design agents:** read the slide's entry in the brief, then the deck standard, then the
live slide. If the story changes, change the brief first; a new number goes in the fact sheet
first. One editor on the live deck at a time. Log each pass in `docs/5_agent_log.md`.

## Poster

`poster.html` and `linkedin.html` are first drafts, rebuilt to [DESIGN.md](DESIGN.md) after
the deck's content is approved. Render from the repo root:

```bash
uv run --no-project --with "playwright==1.60.0" python docs/showcase/render.py
```

## Source files

| Area | File | What it gives us | Poster | Deck |
| --- | --- | --- | --- | --- |
| Overview | [README.md](../../README.md) | Pitch, features, tech stack, live demo link | Yes | Yes |
| Product brief | [1_brief.md](../1_brief.md) | The problem and who it is for | | Yes |
| Architecture | [2_architecture.md](../2_architecture.md) | The request pipeline and components | | Yes |
| The four agents | [agents/](../agents/) | One page per agent | Yes | Yes |
| Decisions | [3_decisions.md](../3_decisions.md) | Quality targets (DEC-25) and fixes (DEC-26 to DEC-28) | | Yes |
| Meal quality | [7_meal_quality.md](../7_meal_quality.md) | Method, targets, the 10 → 72 of 72 table | Yes | Yes |
| Benchmark report | [baseline.md](../meal_quality/baseline.md), [meal_quality_baseline.py](../../scripts/meal_quality_baseline.py) | Every plan's row; the script that reproduces it | | Yes |
| Calorie model | [metrics.json](../../models/calorie_expenditure/metrics.json), [training notebook](../../notebooks/calorie_expenditure_kaggle_training.ipynb) | R², MAE, training rows | | Yes |
| Recipes | [meals.json](../../data/meal_corpus/meals.json) | The 34 curated recipes | | Yes |
| App design | [8_design.md](../8_design.md), [design screens](../assets/design/), [prototype](../design/prototype/) | You → Craving → Your plan; the Chicken Fried Rice plan | Yes | Yes |
| Brand assets | [tailwind.config.js](../../frontend/tailwind.config.js), [logo-mark.svg](../../frontend/src/assets/brand/logo-mark.svg), [logo-wordmark.svg](../../frontend/src/assets/brand/logo-wordmark.svg), [palette.svg](../assets/design/palette.svg) | Colours, fonts, the plate mark | Yes | Yes |
| Screenshots | [assets/screenshots/](../assets/screenshots/) | React and Streamlit captures (React ones show the older dashboard) | | Yes |
| Engineering | [openapi.json](../openapi.json), [ci.yml](../../.github/workflows/ci.yml), [deploy.yml](../../.github/workflows/deploy.yml), [6_deployment.md](../6_deployment.md) | API contract, CI, Cloud Run | | Yes |
| Live demo | <https://tuannm3812-ai-meal-planner.streamlit.app/> | Where readers try it; the QR target | Yes | Yes |
| First drafts | this folder: `poster.html`, `linkedin.html`, `showcase.css`, `render.py`, the two PNGs, `linkedin_post.md` | To be rebuilt to this brief | Yes | |

## Fact sheet

Quote only these numbers, as worded here. Checked against `main` at `b93a799`
on 2026-11-05.

| Claim | Number | Source |
| --- | --- | --- |
| Test plans meeting the quality targets | 72 of 72, up from 10 | 7_meal_quality.md §2 |
| How it got there | 10 → 41 (portion balancing) → 47 (honest fallback) → 72 (cooking fat in six recipes, plus a rounding retry) | same |
| The targets | Calories within 10%; protein 10–35%, carbs 45–65%, fat 20–35% of energy (adult AMDR) | same, §1 (DEC-25) |
| Calorie accuracy | Median deviation 0.3%, worst 9.9% | same, §2 |
| Safety checks | 5 of 5 guardrail cases behave as designed, including refusals | same |
| Benchmark limits | Project's own offline benchmark, no provider keys; AMDR is a daily reference applied to one meal | 7_meal_quality.md §1 |
| Benchmark size | 72 requests: 12 cravings × 4 body profiles, plus 6 cravings × 4 diet or health limits | same, §1 |
| Calorie model | Predicts exercise calories: validation R² 0.996, MAE 2.2 kcal; dataset of 750,000 rows (20% held out, then refit on all) | metrics.json, agents/calorie_expenditure_agent.md |
| Meal target | Exercise calories + BMR-based estimate, goal +250 or −400 kcal (subject to the floor), then 28% of the daily budget, kept to 350–850 kcal | calorie_expenditure_agent.md, meal_recommendation_agent.py |
| Recipe library | 34 curated recipes | meals.json |
| Example plan, design | Chicken Fried Rice: 629 kcal against 625; 42 g protein, 71 g carbs, 18 g fat (27/46/27%) | 8_design.md §2 |
| Example plan, real run | Chicken Fried Rice: 694 kcal against 691; 48 g protein, 78 g carbs, 19 g fat (28/46/26%); 3 of 6 ingredients estimated; estimated shopping total $24.50 | Local run, 2026-11-06, no provider keys; slides/captures/2026-11-06-plan.json |
| One dish, four people | Chicken fried rice: 363 kcal (older woman, losing), 694 (active woman, maintaining), 809 (average man, maintaining), 850 (large athlete, gaining); all meet the targets | meal_quality/baseline.json |
| Safety floor | Weight-loss budgets apply a floor of 1,200 kcal for women or 1,500 for men, capped at estimated expenditure; a warning explains when it applies | DEC-24, calorie_expenditure_agent.py |
| Tests | 598 Python tests, 95% coverage (Claude's full run logged 2026-11-02) | 5_agent_log.md |
| Benchmark split | 61 matched and 11 fallback plans; 68 of 72 include an estimated ingredient | 7_meal_quality.md §2 |

After PR #43 merges, recheck the wider report and a dated test run, then update
this sheet. Until then the wider by-name check stands at 49 of 68.
