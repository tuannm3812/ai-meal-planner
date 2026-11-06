# Pending tasks

Everything not finished yet, so it can be checked and picked up later. Started 7 November 2026.
Tick a box when the work is merged or done, and add a date.

## Showcase

- [ ] **Mike:** add `STREAMLIT_DEMO_MODE = "1"` to the demo's Secrets in Streamlit, then scan the QR code from a phone. Today the demo opens with demo mode off and shows "Could not connect to the API".
- [ ] Bring the approved slides into the live v4 deck with File > Import slides, then confirm the speaker notes came across.
- [ ] Merge PR #44 once the deck is approved.
- [ ] Rebuild the poster and LinkedIn image to the new standards, and fix the LinkedIn post wording ("filters run first", "590+").
- [ ] Export the release PDF from the live deck.
- [ ] Run Codex's review of the seed text, notes and revised standards (requests are in `docs/5_agent_log.md`).
- [ ] **Mike:** delete the old Drive copies, keeping the v4 Slides deck and the v4 `.pptx`.
- [ ] Update the design brief doc, which lags this repo.

## Product, in priority order

- [ ] **Storage:** add database migrations (Alembic). Needed before any deployment holds real data. `docs/4_next_steps.md` §7.1.
- [ ] **Hosting:** create the GCP project and deploy to Cloud Run, then confirm a real trace arrives. `docs/6_deployment.md` §1.
- [ ] **Data:** run the benchmark with USDA keys, so nutrition is checked independently of the local tables.
- [ ] **Recipes:** grow the library from 34 to 75–100 recipes. It gates the vector database. `docs/4_next_steps.md` §7.9.
- [ ] **Prices:** connect live store prices. 4 of 6 items in the example plan use category prices.
- [ ] **Learning:** use saved meals and ratings in ranking. They are collected but unused. `docs/4_next_steps.md` §7.10.
- [ ] **People:** test with users, and ask a dietitian to review the rules and targets.

## Accuracy

- [ ] **Calorie model:** ask for real exercise details, or stop adding exercise on top of the activity multiplier. The meal flow uses defaults (30 minutes, 100 bpm), so activity may count twice.
- [ ] **Diet rules:** move from matching ingredient names to tagged allergens. Name matching missed soy sauce until DEC-31.
- [ ] **Meal target:** record why it is 28% of the day, and review the cap for large budgets. The large athlete's meal is 19% of the day.
- [ ] **Low-carb preference:** it favours no meal now, because no recipe is low-carb (DEC-30).

## Repo clean-up

- [ ] Decide what to do with the 75 records in local `database/meal_history.json` before ever running `scripts/migrate_json_to_sqlite.py`, which isn't idempotent.
- [ ] Raise `ProfileNotFound` or remove it. An unknown `user_id` silently gets the default profile.
- [ ] Add accounts. Endpoints that take a `user_id` take it on trust. `docs/4_next_steps.md` §7.7.
- [ ] Reword the app's step 1 panel, which says a trained model "estimates the energy you burn in a day".
