# Backend-First Product Roadmap

## Product Direction

Build the meal planner as a backend-first AI data product. The first usable release should expose a reliable API and a simple Streamlit operator UI before investing in a polished React frontend.

## Agent Responsibilities

### 1. Calorie Expenditure Agent

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

### 2. Meal Recommendation Agent

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

### 3. Nutrition Verification Agent

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

## Workflow

1. User submits profile, health constraints, dietary preferences, and meal goal.
2. Calorie Expenditure Agent predicts expenditure and meal calorie budget.
3. Meal Recommendation Agent retrieves and adapts meals using RAG.
4. Nutrition Verification Agent validates ingredient nutrition through USDA.
5. Orchestrator compares generated estimate versus verified total.
6. If the verified total is outside tolerance, the meal agent revises portions.
7. API returns the final meal plan with verification metadata.

## MVP Scope

- FastAPI backend with typed request and response schemas.
- Streamlit app for demos and manual testing.
- File-backed local storage during prototyping.
- Offline model artifact for calorie expenditure prediction.
- USDA verification with local fallback estimates.
- RAG over a small curated meal corpus before adding a large recipe database.

## Later Scope

- Managed database for profiles, plans, and audit logs.
- Vector database for meal retrieval.
- Model registry for calorie expenditure models.
- React frontend refinement.
- Supermarket and grocery list agent.
- User feedback loop for preference learning.
