# Showcase brief — poster and slide deck

**Status: draft for Mike, 2026-11-05.** The working copy is the Claude doc
<https://claude.ai/artifact/D5bMLYdKiMp35fKEsVR9Mb> (it also has the poster
wireframe). This file mirrors it so the brief lives next to the drafts.
Mike's open decisions are in §9; nothing here is built to them yet.

## 1. Purpose and audience

Two outputs share one design system and one set of facts: a one-page poster
(plus a LinkedIn version) and a 12-slide deck. The poster is the short version;
the deck is the same story with the evidence behind it.

The poster should leave anyone, technical or not, with one sentence: **say what
you crave, and you get one meal sized to you, with every number checked.**
Everything else supports that line or is cut.

- **Who reads it:** recruiters and hiring managers on LinkedIn or a portfolio,
  other engineers, and people with no tech background.
- **How long they look:** about 5 seconds for the headline and picture, 30 if
  it holds them. A first glance must work without reading small text.
- **Change from the first draft:** the draft in this folder has five sections
  and about 250 words. The brief cuts it to four blocks and about 90 words and
  moves the engineering detail into the LinkedIn post text.

The design system is the app's existing Kitchen green identity, from
`frontend/tailwind.config.js` and the brand guidelines draft
(`docs/9_brand_guidelines.md`, not yet committed).

## 2. Source files

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

Render the drafts from the repo root (fonts load from `frontend/node_modules`,
so run `npm install` in `frontend/` first):

```bash
uv run --no-project --with "playwright==1.60.0" python docs/showcase/render.py
```

## 3. Fact sheet

Quote only these numbers, as worded here. Checked against `main` at `b93a799`
on 2026-11-05.

| Claim | Number | Source |
| --- | --- | --- |
| Test plans meeting the quality targets | 72 of 72, up from 10 | 7_meal_quality.md §2 |
| How it got there | 10 → 41 (portion balancing) → 47 (honest fallback) → 72 (cooking fat in six recipes) | same |
| The targets | Calories within 10%; protein 10–35%, carbs 45–65%, fat 20–35% of energy (adult AMDR) | same, §1 (DEC-25) |
| Calorie accuracy | Median deviation 0.3%, worst 9.9% | same, §2 |
| Safety checks | 5 of 5 guardrail cases behave as designed, including refusals | same |
| Benchmark size | 72 requests: 12 cravings × 4 body profiles, plus 6 cravings × 4 diet or health limits | same, §1 |
| Calorie model | R² 0.996, mean error 2.2 kcal, 750,000 training rows | metrics.json |
| Recipe library | 34 tested recipes | meals.json |
| Example plan | Chicken Fried Rice: 629 kcal against 625; 42 g protein, 71 g carbs, 18 g fat (27/46/27%) | 8_design.md §2 |
| Safety floor | Weight-loss plans never below 1,200 kcal a day for women or 1,500 for men | AGENTS.md (DEC-24) |
| Tests | 596 Python tests, 95% coverage (last full run logged 2026-10-08) | 5_agent_log.md |

If PR #43 merges, two numbers change: the wider by-name recipe check goes from
49 to 68 of 68, and the test count to 618. Use them only after it merges.

## 4. Colour palette

A mostly neutral page, dark green for weight, tomato for one thing only.
Roughly 70% ground and white, 20% ink, under 10% tomato.

| Swatch | Token | Hex | Use it for | On the poster |
| --- | --- | --- | --- | --- |
| Ground | `ground` | #F6F7F2 | Page background | Poster background |
| Surface | `surface` | #FFFFFF | Cards | Meal card, info cards |
| Ink | `ink` | #15291F | Headings, body, dark panels | Headline, 72/72 panel, footer |
| Muted | `muted` | #4B5B52 | Supporting text | Captions |
| Line | `line` | #DDE3DA | Thin borders | Card borders |
| Tomato | `accent` | #C8431F | Logo and the single highlight | Logo, the words "fits you" |
| Tomato text | `accent-text` | #B23A17 | Small accent text | Section labels |
| Success | `success-bg` / `success-fg` | #E3EFE6 / #1B5E3F | Positive badges with a label | "On target", progress bars |
| Protein / Carbs / Fat | `protein` / `carbs` / `fat` | #2F6FAB / #9A6A12 / #7A4E9C | That macro's data only | Macro bars |

Macro colours mean only their macro, green never implies "medically safe", and
tomato never means an error.

## 5. Typography

Bricolage Grotesque for anything big, Inter for anything read, both already
bundled with the app. At most four sizes on one poster.

| Role | Typeface | Weight | Poster (1200 px wide) | LinkedIn (1080 px wide) |
| --- | --- | --- | --- | --- |
| Headline | Bricolage Grotesque | 800 | 64–76 px | 76–84 px |
| Big number | Bricolage Grotesque | 800 | 96–112 px | 84 px |
| Section title | Bricolage Grotesque | 700 | 28–32 px | not used |
| Body and captions | Inter | 400 / 500 | 16–20 px | 18–22 px |
| Section label | Inter | 700, caps, wide spacing | 14 px | 14 px |

Units beside numbers (629 kcal, 42 g), sentence case, body lines under about
60 characters.

## 6. Icon and logo

One icon: the **plate mark**, a tomato ring with a tomato dot
(`frontend/src/assets/brand/logo-mark.svg`, also the favicon). Put it beside
"AI Meal Planner" top left; alone only where space is tiny. Tomato on a light
background, own proportions, clear space of a quarter of its width, never under
24 px. The React app uses no icon set, so numbered circles stand in for icons.

## 7. Poster: key messages and layout

| # | Message | Proposed wording | What shows it |
| --- | --- | --- | --- |
| 1 | What it does | **Say what you crave. Get a meal that fits you.** One meal sized to your body and goal, plus the shopping list. | Headline and subtitle |
| 2 | It is real | For your craving "chicken fried rice": 629 kcal against a 625 kcal target, all macros in range. | The meal card (the only highlighted block) |
| 3 | How it works | Estimate your calories → Find a matching recipe → Check the nutrition → Build the shopping list. | Four numbered steps in a row |
| 4 | It is measured | **72 of 72** test meal plans hit their calorie target and healthy macro ranges, up from 10. | One big number on the ink panel |

Footer: live demo (as a QR code), GitHub link, one tech line. Leave off the
poster: test counts, R² and error metrics, OpenTelemetry, Cloud Run, API keys,
the acronym AMDR, agent class names, the intermediate 41 and 47.

Layout, top to bottom in one column: logo bar, headline, meal card, four steps,
72/72 panel, footer. Poster 1200 × 1800 px (2:3, prints at A3 or A2); LinkedIn
1080 × 1350 px (4:5) with the steps and 72/72 side by side. Both exported at 2×;
at least 64 px margins, 24 px between blocks, 16–20 px card corners.

## 8. Slide deck

12 slides for a 10-minute portfolio or interview talk; each title is the
slide's point, at most about 30 words on screen, the rest in speaker notes.

| # | Slide title | What's on it | Visual | Source |
| --- | --- | --- | --- | --- |
| 1 | AI Meal Planner: say what you crave, get a meal that fits you | Name, pitch, Mike's name | Plate mark, demo QR | README.md |
| 2 | Picking a meal is easy; sizing it to your body is not | The problem, who it is for | Three pain points | 1_brief.md |
| 3 | One craving in, one meal and a shopping list out | The three-step flow | The three design screens | 8_design.md, assets/design/ |
| 4 | Four agents work in sequence and return one typed answer | Calorie → recipe → nutrition → shopping | Pipeline diagram | 2_architecture.md, agents/ |
| 5 | A model trained on 750,000 rows sets each meal's calorie target | R² 0.996, mean error 2.2 kcal; goal and floor | Big numbers | metrics.json, notebook |
| 6 | Diet and allergy filters run first, then search finds the closest tested recipe | 34 recipes; says so when nothing matches | Filter funnel | meal_recommendation_agent.md, meals.json |
| 7 | Every ingredient is checked against USDA, and estimates are labelled | USDA first, then FatSecret and local tables | Ingredient list with badges | nutrition_verification_agent.md |
| 8 | We defined a good meal before trying to improve one | Targets and the 72-request benchmark | Target bands | 7_meal_quality.md §1 |
| 9 | Three fixes took the planner from 10 to 72 of 72 | What each fix changed | Step chart 10 → 41 → 47 → 72 | 7_meal_quality.md §2, baseline.md |
| 10 | It is built like a product, not a notebook | API contract, tests, keys and rate limits, tracing, Cloud Run | Six tiles | openapi.json, ci.yml, 6_deployment.md |
| 11 | What comes next, and what it is not yet | Backlog items and honest limits | Short list | 4_next_steps.md |
| 12 | Try it and read the code | Demo and GitHub links | Demo QR, meal card | Live demo, GitHub |

## 9. Decisions for Mike

Poster:

- Format: portrait 2:3 for print and screen (recommended), or screen only.
- Headline: keep "Say what you crave. Get a meal that fits you." (recommended).
- QR code to the live demo in the footer: yes (recommended) or no.
- Step icons: numbered circles only (recommended), or one outline icon per step.
- Engineering detail: moved to the LinkedIn text (recommended), or one footer line.

Deck:

- Occasion: a 10-minute portfolio or interview talk (recommended), or longer.
- Format: a Claude slides artifact that downloads as PowerPoint or PDF
  (recommended), or a .pptx built directly.
- Order: finish the poster first, then the deck (recommended), or both together.
