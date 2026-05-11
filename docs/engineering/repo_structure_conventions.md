# Repository Structure & Conventions

## Target Structure

```text
ai-meal-planner/
|-- backend/
|   |-- app/
|   |   |-- api/
|   |   |   |-- routes/
|   |   |   `-- dependencies.py
|   |   |-- agents/
|   |   |   |-- calorie_expenditure_agent.py
|   |   |   |-- meal_recommendation_agent.py
|   |   |   |-- nutrition_verification_agent.py
|   |   |   `-- supermarket_agent.py
|   |   |-- core/
|   |   |   |-- config.py
|   |   |   `-- logging.py
|   |   |-- ml/
|   |   |   |-- calorie_model.py
|   |   |   |-- features.py
|   |   |   `-- training.py
|   |   |-- rag/
|   |   |   |-- embeddings.py
|   |   |   |-- retriever.py
|   |   |   `-- meal_corpus.py
|   |   |-- repositories/
|   |   |   |-- meal_plans.py
|   |   |   `-- user_profiles.py
|   |   |-- schemas/
|   |   |   |-- meal_plan.py
|   |   |   |-- nutrition.py
|   |   |   `-- user_profile.py
|   |   |-- services/
|   |   |   |-- usda_client.py
|   |   |   `-- meal_planning_service.py
|   |   `-- main.py
|   |-- tests/
|   |-- requirements.txt
|   `-- README.md
|-- data/
|   |-- external/
|   |-- processed/
|   `-- raw/
|-- docs/
|   |-- agents/
|   |-- architecture/
|   |-- engineering/
|   `-- product/
|-- frontend/
|-- notebooks/
|-- streamlit_app/
|   `-- app.py
|-- models/
|   |-- calorie_expenditure/
|   `-- README.md
|-- .env.example
|-- pyproject.toml
`-- README.md
```

## Current-to-Target Migration

The repository now follows the target package layout. Continue tightening it incrementally:

1. Move shared Pydantic models into `backend/app/schemas/`.
2. Move API route handlers out of `main.py` into `backend/app/api/routes/`.
3. Extract external API calls into `backend/app/services/`.
4. Add reusable calorie model feature transforms under `backend/app/ml/`.
5. Add retrieval-backed meal generation under `backend/app/rag/`.
6. Add tests as each module is moved.

## Naming

- Agent classes end with `Agent`, for example `CalorieExpenditureAgent`.
- Service classes end with `Service` or `Client`, for example `UsdaFoodDataClient`.
- Pydantic request models end with `Request`.
- Pydantic response models end with `Response`.
- Database abstractions end with `Repository`.
- Model artifacts include semantic versions, for example `calorie_expenditure_v0.1.0.joblib`.

## API Conventions

- Prefer nouns in route paths: `/meal-plans`, `/nutrition/verify`, `/calorie-expenditure/predict`.
- Include `request_id`, `model_version`, and `metadata` in AI or ML responses.
- Never return raw LLM text as the primary contract. Return typed JSON.
- Include confidence and warnings for generated, predicted, or externally matched values.
- Keep health-sensitive fields explicit and auditable.

## Data & Model Conventions

- Do not commit raw Kaggle datasets or local generated history.
- Put raw local datasets under `data/raw/`.
- Put cleaned feature tables under `data/processed/`.
- Put third-party reference files under `data/external/`.
- Save trained models under `models/`.
- Track model metrics in a small JSON file next to the artifact.

## Testing Conventions

- Unit test schemas, feature transforms, calorie prediction inference, and nutrition scaling.
- Mock external APIs by default.
- Add one integration test for the full meal-planning orchestration.
- Keep deterministic fallback tests so demos work without paid API keys.

## Streamlit Convention

Use Streamlit as the first live interface. It should call the same backend service layer as FastAPI, not duplicate agent logic. Treat it as an operator/demo UI until the React frontend is ready.
