# Meal Vector RAG

## Goal

Reduce Gemini usage by retrieving structured meal templates before calling an LLM.

## Current Flow

```text
User craving + preferences
-> hard safety filter for allergies, dietary constraints, and health conflicts
-> local TF-IDF vector search over data/meal_corpus/meals.json
-> structured meal template with known ingredient substitutions
-> portion scaling against meal calorie target
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

The current seed corpus contains 34 curated meal templates across bowls, salads, wraps, pasta, breakfast, soups, vegetarian, vegan, seafood, poultry, turkey, beef, low-sodium, and high-protein options.

Each item contains:

- `meal_id`
- `name`
- `description`
- `tags`
- `dietary_flags`
- `avoid_conditions`
- `ingredients`

Hard filtering happens before vector scoring. Meals that conflict with selected health
conditions are removed, and ingredient-level allergy conflicts are removed unless a
known substitution can make the meal safe.

Known substitution examples include wheat buns to gluten-free buns, soy sauce to
coconut aminos, whole egg to tofu, dairy yogurt to soy yogurt, and peanut butter to
sunflower seed butter.

## API Contract

When a meal is selected through retrieval, the meal plan includes:

```json
{
  "metadata": {
    "source": "local_vector_rag_meal_corpus",
    "confidence": 0.72
  },
  "retrieval": {
    "query": "fried rice",
    "retriever": "tfidf_vector_retriever_v0.1",
    "selected_meal_id": "chicken_fried_rice",
    "selected_score": 0.72,
    "matched_terms": ["fried", "rice"],
    "substitutions": [],
    "candidates": []
  },
  "portion_scaling": {
    "target_meal_calories": 820,
    "estimated_template_calories": 510.4,
    "scale_factor": 1.6
  }
}
```

The UI should use `metadata.source` for high-level display and `retrieval` for debugging/evaluation.

## Next Improvements

- Expand corpus coverage to 50-100 curated meals first, then move to a larger normalized recipe corpus.
- Evaluate external recipe sources such as Food.com/RecipeNLG-style datasets or a licensed recipe API, then verify all nutrition through USDA FoodData Central.
- Add richer substitution coverage for tree nuts, halal, kosher, and low-FODMAP.
- Add LLM adaptation only after retrieval when needed.
- Add retrieval evaluation examples for common cravings.

## Data Source Guidance

Use two layers:

1. Recipe retrieval corpus: meal names, tags, ingredients, dietary labels, cuisine, and preparation context.
2. Nutrition verification source: USDA FoodData Central or another licensed nutrition analysis provider.

Do not assume a recipe dataset has reliable nutrition. Treat recipe datasets as retrieval candidates and run their ingredients through the nutrition verification agent.
