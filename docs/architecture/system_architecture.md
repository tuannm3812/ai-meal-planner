# System Architecture & Data Flow

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
