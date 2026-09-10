# System Architecture & Data Flow

> **Known divergence — as of 2026-09-10 this document describes the target, not the
> current build.** The orchestrator coordinating the agents in §3 does not exist:
> there is no `services/meal_planning_service.py` and no DI container, and each
> agent is constructed directly in `backend/app/main.py`. In §4, step 3 (Calorie
> Prediction) is not wired into meal planning, step 6 (Revision Loop) is not
> implemented at all, and step 8 (Storage) persists the meal and feedback but no
> embeddings. Phase 1 lands the orchestrator, the calorie wiring and the
> reconciliation loop — see [`4_next_steps.md`](4_next_steps.md) §1 and
> [the design spec §6](superpowers/specs/2026-09-10-refactor-and-standards-alignment-design.md).
> **Remove this note when Phase 1 lands.**

## 1. High-Level Overview

This project is a backend-first, multi-agent meal planning application. It combines ML calorie expenditure prediction, retrieval-backed meal recommendation, and authoritative nutrition verification.

The backend owns the product contracts. Streamlit is the recommended first live interface for demos and validation. The React frontend can be refined after the backend schemas, model outputs, and verification workflow are stable.

## 2. Technology Stack

* **Backend**: Python 3.11+, FastAPI, Pydantic.
* **Demo UI**: Streamlit.
* **Frontend**: React, Vite, Tailwind CSS for the later polished UI.
* **ML**: scikit-learn baseline first; evaluate LightGBM, XGBoost, CatBoost, or RandomForest for calorie expenditure regression.
* **AI/LLM**: Gemini or another model provider for controlled meal adaptation and explanation.
* **RAG**: Local corpus first, then vector database for scalable meal retrieval.
* **Nutrition Data**: USDA FoodData Central API, with optional fallback providers and local estimates.
* **Infrastructure**: Containerized backend, deployable to Cloud Run or another managed container runtime.
* **Database**: Start file-backed for local pilots; move to Postgres, Firestore, or another managed store when user state and auditability matter.

## 3. Multi-Agent Orchestration

The orchestrator coordinates three core agents and keeps each agent's responsibility narrow.

### A. Calorie Expenditure Agent

* **Trigger**: Receives user profile, health constraints, and activity inputs.
* **Action**: Predicts calorie expenditure using a trained regression model based on the Kaggle Playground Series S5E5 calorie expenditure dataset.
* **Output**: Returns calorie budget, confidence, model version, and warnings.

### B. Meal Recommendation Agent

* **Trigger**: Receives calorie budget, dietary restrictions, allergies, preferences, disliked foods, cuisine, and prep constraints.
* **Action**: Retrieves candidate meals from the meal corpus, then uses GenAI only to adapt and rank the recommendation.
* **Output**: Returns a structured meal plan with ingredient names, gram quantities, retrieval sources, and estimated calories.

### C. Nutrition Verification Agent

* **Trigger**: Receives the exact ingredient array from the Meal Recommendation Agent.
* **Action**: Queries USDA FoodData Central, normalizes portions, and calculates verified nutrition totals.
* **Output**: Returns scaled calories, protein, carbohydrates, fat, confidence, warnings, and unmatched items.

### Later Agent: Supermarket Agent

The supermarket workflow should remain a later-stage add-on. It can map verified ingredient lists to local grocery items once the core nutrition workflow is trustworthy.

## 4. Data Flow Protocol

1. **User Input**: User submits profile, conditions, preferences, and meal goal.
2. **State Retrieval**: Backend fetches stored profile and preference history.
3. **Calorie Prediction**: Calorie Expenditure Agent predicts expenditure and meal budget.
4. **Meal Retrieval and Adaptation**: Meal Recommendation Agent retrieves candidate meals and adapts the best option.
5. **Nutrition Verification**: Nutrition Verification Agent verifies each ingredient through USDA and scales nutrition by portion.
6. **Revision Loop**: If verified calories are outside tolerance, the orchestrator requests portion adjustment.
7. **Response**: Backend returns typed JSON with request metadata, model versions, nutrition sources, confidence, and warnings.
8. **Storage**: Final meal, feedback, and embeddings are saved for future recommendation.

## 5. Package layout

The target package layout. Directories that do not exist yet are created by the
phase that needs them; the remaining moves are tracked in
[`4_next_steps.md`](4_next_steps.md) §5.

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
|   |   |   |-- requests.py
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
|-- render.yaml
|-- runtime.txt
|-- data/
|   |-- external/
|   |-- processed/
|   `-- raw/
|-- docs/
|   |-- 0_coding_standards.md
|   |-- 1_brief.md
|   |-- 2_architecture.md
|   |-- 3_decisions.md
|   |-- 4_next_steps.md
|   |-- 5_agent_log.md
|   |-- agents/
|   |-- architecture/
|   `-- superpowers/
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

## 6. Detail references

Per-component detail lives in the two retained subfolders. A topic earns a
subfolder once it has two or more files; both qualify.

- [`agents/calorie_expenditure_agent.md`](agents/calorie_expenditure_agent.md)
- [`agents/meal_recommendation_agent.md`](agents/meal_recommendation_agent.md)
- [`agents/nutrition_verification_agent.md`](agents/nutrition_verification_agent.md)
- [`agents/supermarket_agent.md`](agents/supermarket_agent.md) — note: this doc
  describes MCP-based mapping and inventory tooling that is **not implemented**;
  the supermarket agent currently uses local reference tables (see
  `_locate_nearest_store`, `_map_inventory_and_price`,
  `_estimate_category_and_price` in `backend/app/agents/supermarket_agent.py`),
  and the doc is retained as design intent, not a description of the current build.
- [`architecture/vector_rag.md`](architecture/vector_rag.md) — retrieval backend
  selection and the TF-IDF to embeddings transition
- [`architecture/ai_meal_planner_architecture.excalidraw`](architecture/ai_meal_planner_architecture.excalidraw)
  — editable source for the architecture flow diagram
