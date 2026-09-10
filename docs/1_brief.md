# Project Brief — ai-meal-planner

What is being built, for whom, and what done looks like. Architecture is in
[`2_architecture.md`](2_architecture.md); everything deferred is in
[`4_next_steps.md`](4_next_steps.md).

## 1. Product Direction

Build the meal planner as a backend-first AI data product. The first usable release should expose a reliable API and a simple Streamlit operator UI before investing in a polished React frontend.

## 2. Positioning

This is a **self-directed portfolio project first**, built with an intended path to
real users. That ordering decides trade-offs: the design must not have to be thrown
away when real users arrive, but no work is justified purely by production concerns
that no current user has (managed Postgres, authentication, SLAs). Recorded as DEC-1
in [`3_decisions.md`](3_decisions.md).

**No rubric or external marking criteria apply.** There is no assignment brief, no
grader and no submission deadline. The only standard the work answers to is the
master coding standard at `~/Documents/GitHub/coding-standards/coding_standards.md`
and the project deltas in [`0_coding_standards.md`](0_coding_standards.md).

## 3. What done looks like

The MVP is done when all of the following hold. Each is checkable, not aspirational.

- [ ] The FastAPI backend serves every endpoint with a typed request **and** a typed
      response schema, so `/docs` shows full contracts rather than free-form JSON.
- [ ] The Streamlit app drives the full flow — profile in, verified meal plan out —
      without a developer needing to read the code first.
- [ ] File-backed local storage persists profiles, plans and feedback across restarts
      and is swappable behind an interface, so the prototype store is not load-bearing.
- [ ] `/generate-meal-plan` demonstrably consumes the offline calorie model's budget:
      the shipped artifact is loaded at startup and its
      `meal_calorie_budget_kcal` reaches the recommendation step.
- [ ] Nutrition verification calls USDA FoodData Central and, when the provider is
      unavailable, falls back to local estimates with the degradation reported in
      `warnings` rather than hidden.
- [ ] RAG retrieval runs over the curated local meal corpus (34 templates as of
      2026-09-10) with no large recipe database required to get a plan.

As of 2026-09-10 items 1, 3 and 4 are open. The FastAPI backend has no
`response_model` on any route and all 8 routes return `dict[str, Any]` (item 1);
`repositories/storage.py` is three plain classes with no `Protocol` or ABC
boundary (item 3); and the calorie model is trained, shipped and tested in
isolation, but `/generate-meal-plan` does not yet use its budget (item 4). Closing
item 4 is the first task of Phase 1 — see [`4_next_steps.md`](4_next_steps.md).

## 4. Agent Responsibilities

### 4.1 Calorie Expenditure Agent

**Goal:** predict daily energy expenditure and produce a calorie budget for meal planning.

**Training source:** Kaggle Playground Series S5E5, "Predict Calorie Expenditure".

**Model type:** supervised regression. Start with a simple baseline, then compare tree-based models such as LightGBM, XGBoost, CatBoost, or RandomForest.

**Expected input contract:**

- Demographics: age, sex, height, weight.
- Activity physiology: duration, heart rate, body temperature where available.
- User health context: goals, conditions, dietary restrictions, allergies, medications, and clinician constraints.

**Output contract:**

- `estimated_daily_expenditure_kcal`
- `meal_calorie_budget_kcal`
- `model_version`
- `confidence`
- `warnings`

**Important boundary:** health conditions should constrain recommendations, not be treated as medical diagnosis. The app should clearly say that it provides nutrition planning support, not medical advice.

### 4.2 Meal Recommendation Agent

**Goal:** recommend a daily meal plan from user preferences, restrictions, calorie budget, and prior successful meals.

**Recommended architecture:** use RAG before free-form generation.

RAG should retrieve structured meal candidates from a curated recipe/meal knowledge base, then use the LLM only to adapt, rank, and explain the final plan. This reduces hallucinated ingredients, improves repeatability, and gives the nutrition verifier cleaner inputs.

**Retrieval inputs:**

- Food preferences and disliked foods.
- Allergies and restrictions.
- Target calories and macro ranges.
- Cuisine, budget, prep time, and location if available.

**Output contract:**

- `meal_name`
- `meal_type`
- `ingredients[]`
- `portion_grams`
- `estimated_calories_kcal`
- `retrieved_sources[]`
- `generation_notes`

### 4.3 Nutrition Verification Agent

**Goal:** verify calories and macros using authoritative nutrition data.

**Primary source:** USDA FoodData Central API.

**Process:**

1. Normalize ingredient names and units.
2. Match each ingredient to USDA records.
3. Convert servings to grams.
4. Calculate calories and macros per portion.
5. Return confidence, warnings, and unmatched items.

**Output contract:**

- `ingredients_macros[]`
- `total_calories_kcal`
- `total_protein_g`
- `total_carbs_g`
- `total_fat_g`
- `verification_confidence`
- `warnings`

## 5. Workflow

1. User submits profile, health constraints, dietary preferences, and meal goal.
2. Calorie Expenditure Agent predicts expenditure and meal calorie budget.
3. Meal Recommendation Agent retrieves and adapts meals using RAG.
4. Nutrition Verification Agent validates ingredient nutrition through USDA.
5. Orchestrator compares generated estimate versus verified total.
6. If the verified total is outside tolerance, the meal agent revises portions.
7. API returns the final meal plan with verification metadata.

Steps 2, 5 and 6 are unimplemented as of 2026-09-10 and are the contract Phase 1 is
built against. This list is the reference for the product-level workflow;
[`2_architecture.md`](2_architecture.md) §4 (Data Flow Protocol) legitimately
restates the same flow in implementation terms and should be kept in sync with it
rather than treated as a duplicate to delete.

## 6. MVP Scope

- FastAPI backend with typed request and response schemas.
- Streamlit app for demos and manual testing.
- File-backed local storage during prototyping.
- Offline model artifact for calorie expenditure prediction.
- USDA verification with local fallback estimates.
- RAG over a small curated meal corpus before adding a large recipe database.

Everything beyond this scope — managed database, vector database, model registry,
supermarket agent, feedback-driven ranking — is in
[`4_next_steps.md`](4_next_steps.md).
