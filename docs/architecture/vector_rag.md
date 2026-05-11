# Meal Vector RAG

## Goal

Reduce Gemini usage by retrieving structured meal templates before calling an LLM.

## Current Flow

```text
User craving + preferences
-> local TF-IDF vector search over data/meal_corpus/meals.json
-> structured meal template
-> USDA/FatSecret/local nutrition verification
-> shopping list fallback estimates
```

If the retriever finds a strong match, Gemini is not called.

## Why TF-IDF First

TF-IDF keeps local and Streamlit deployment simple:

- No embedding API quota.
- No large model download.
- No vector database service.
- Deterministic behavior in tests.

The interface is intentionally isolated in `backend/app/rag/retriever.py`, so the implementation can later be replaced with sentence embeddings or a managed vector database.

## Corpus

Meal templates live in:

```text
data/meal_corpus/meals.json
```

Each item contains:

- `meal_id`
- `name`
- `description`
- `tags`
- `dietary_flags`
- `avoid_conditions`
- `ingredients`

## Next Improvements

- Expand corpus coverage to 50-100 meals first, then move to a larger normalized recipe corpus.
- Evaluate external recipe sources such as Food.com/RecipeNLG-style datasets or a licensed recipe API, then verify all nutrition through USDA FoodData Central.
- Add calorie-budget portion scaling.
- Add substitution rules for allergies and preferences.
- Add LLM adaptation only after retrieval when needed.
- Add retrieval evaluation examples for common cravings.

## Data Source Guidance

Use two layers:

1. Recipe retrieval corpus: meal names, tags, ingredients, dietary labels, cuisine, and preparation context.
2. Nutrition verification source: USDA FoodData Central or another licensed nutrition analysis provider.

Do not assume a recipe dataset has reliable nutrition. Treat recipe datasets as retrieval candidates and run their ingredients through the nutrition verification agent.
