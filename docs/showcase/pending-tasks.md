# Pending tasks

Everything not finished yet, so the app and the deck can be built side by side. Started 7 November 2026.
Tick a box when the work is merged or done, and add a date.

## Task numbers

P1 to P9 name the tasks. The deck stays free of internal notes, so this table says which slides to
update when a task is done.

| Task | What | Slides to update |
| --- | --- | --- |
| P1 | Turn on demo mode in Streamlit | Remove the wake-up line on 16 if it stays awake |
| P2 | Add database migrations | 14, 15 |
| P3 | Deploy to Cloud Run | Turn the line on 13 green; 12, 14, 15 |
| P4 | Run the benchmark with USDA keys | The bar on 9; estimate counts on 2, 11, 14 |
| P5 | Ask for real exercise details | The worked example and note on 7 |
| P6 | Tag allergens on ingredients | The diet rule limit on 14 |
| P7 | Grow to 75–100 recipes | "34 recipes" across the deck |
| P8 | Connect live store prices | $24.50 on 1, 2, 6 |
| P9 | Use feedback, then test with people | The "Not tested" step on 14 |

## Showcase

- [ ] **P1, Mike:** add `STREAMLIT_DEMO_MODE = "1"` to the demo's Secrets in Streamlit, then scan the QR code from a phone. Today the demo opens with demo mode off and shows "Could not connect to the API".
- [ ] Rebuild the poster and LinkedIn image to the new standards, and fix the LinkedIn post wording ("filters run first", "590+").
- [ ] Export the release PDF from the live deck.
- [ ] Run Codex's review of the seed text, notes and revised standards (requests are in `docs/5_agent_log.md`).
- [ ] Update the design brief doc, which lags this repo.

## Product, in priority order

- [x] **P2 Storage:** add database migrations (Alembic). Done 7 November 2026, DEC-32.
- [ ] **P3 Hosting:** create the GCP project and deploy to Cloud Run, then confirm a real trace arrives. `docs/6_deployment.md` §1.
- [ ] **P4 Data:** run the benchmark with USDA keys, so nutrition is checked independently of the local tables.
- [ ] **P7 Recipes:** grow the library from 34 to 75–100 recipes. It gates the vector database. `docs/4_next_steps.md` §7.9.
- [ ] **P8 Prices:** connect live store prices. 4 of 6 items in the example plan use category prices.
- [ ] **P9 Learning:** use saved meals and ratings in ranking. They are collected but unused. `docs/4_next_steps.md` §7.10.
- [ ] **P9 People:** test with users, and ask a dietitian to review the rules and targets.

## Accuracy

- [ ] **P5 Calorie model:** ask for real exercise details, or stop adding exercise on top of the activity multiplier. The meal flow uses defaults (30 minutes, 100 bpm), so activity may count twice.
- [ ] **P6 Diet rules:** move from matching ingredient names to tagged allergens. Name matching missed soy sauce until DEC-31.
- [ ] **Meal target:** record why it is 28% of the day, and review the cap for large budgets. The large athlete's meal is 19% of the day.
- [ ] **Low-carb preference:** it favours no meal now, because no recipe is low-carb (DEC-30).

## Repo clean-up

- [ ] Decide what to do with the 75 records in local `database/meal_history.json`. They look like test output, so the recommendation is not to import them (agent log, 7 November 2026).
- [ ] Raise `ProfileNotFound` or remove it. An unknown `user_id` silently gets the default profile.
- [ ] Add accounts. Endpoints that take a `user_id` take it on trust. `docs/4_next_steps.md` §7.7.
- [ ] Reword the app's step 1 panel, which says a trained model "estimates the energy you burn in a day".
