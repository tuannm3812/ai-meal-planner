# Showcase poster and slide deck

Everything for the project's showcase. Start here.

| Need | Go to |
| --- | --- |
| Edit the deck | [Live Google Slides deck](https://docs.google.com/presentation/d/1Pm0IzeQQoAXNDdjvKvWIPQUkZCUnHgkgS3YE6-w1zm0/edit) (source of truth for formatting) |
| What each slide says | [slides/BRIEF.md](slides/BRIEF.md) |
| How slides look | [slides/DESIGN.md](slides/DESIGN.md), with [design history](slides/design-history.md) |
| How the poster looks and reads | [DESIGN.md](DESIGN.md) |
| Brand tokens, voice and logo | [root DESIGN.md](../../DESIGN.md) |
| Numbers we may quote | [Fact sheet](#fact-sheet) below |

**For design agents:** read the slide's entry in the brief, then the deck standard, then the
live slide. Change the brief first if the story changes. One editor on the live deck at a
time. Never reimport `deck/` over it; `deck/build_deck.js` and the `.pptx` are the first seed.

The poster, LinkedIn image and `linkedin_post.md` in this folder are first drafts, to be
rebuilt to [DESIGN.md](DESIGN.md). Render them from the repo root (fonts load from
`frontend/node_modules`, so run `npm install` in `frontend/` first):

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
| Recipes | [meals.json](../../data/meal_corpus/meals.json) | The 34 tested recipes | | Yes |
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
| How it got there | 10 → 41 (portion balancing) → 47 (honest fallback) → 72 (cooking fat in six recipes) | same |
| The targets | Calories within 10%; protein 10–35%, carbs 45–65%, fat 20–35% of energy (adult AMDR) | same, §1 (DEC-25) |
| Calorie accuracy | Median deviation 0.3%, worst 9.9% | same, §2 |
| Safety checks | 5 of 5 guardrail cases behave as designed, including refusals | same |
| Benchmark limits | Project's own offline benchmark, no provider keys; AMDR is a daily reference applied to one meal | 7_meal_quality.md §1 |
| Benchmark size | 72 requests: 12 cravings × 4 body profiles, plus 6 cravings × 4 diet or health limits | same, §1 |
| Calorie model | Predicts exercise calories: R² 0.996, mean error 2.2 kcal on validation data, 750,000 training rows | metrics.json, agents/calorie_expenditure_agent.md |
| Meal target | Exercise calories + BMR-based estimate, goal −400 or +250 kcal, then 28% of the daily budget, kept to 350–850 kcal | calorie_expenditure_agent.md, meal_recommendation_agent.py |
| Recipe library | 34 tested recipes | meals.json |
| Example plan | Chicken Fried Rice: 629 kcal against 625; 42 g protein, 71 g carbs, 18 g fat (27/46/27%) | 8_design.md §2 |
| Safety floor | Weight-loss plans never below 1,200 kcal a day for women or 1,500 for men | AGENTS.md (DEC-24) |
| Tests | 598 Python tests, 95% coverage (Claude's full run logged 2026-11-02) | 5_agent_log.md |
| Benchmark split | 61 matched and 11 fallback plans; 68 of 72 include an estimated ingredient | 7_meal_quality.md §2 |

If PR #43 merges, two numbers change: the wider by-name recipe check goes from
49 to 68 of 68, and the test count to 618. Use them only after it merges.
