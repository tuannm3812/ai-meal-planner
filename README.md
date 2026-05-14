# AI Meal Planner

![AI Meal Planner hero](https://assets.epicurious.com/photos/689523e500efe724a5ef8bb5/16:9/w_2560%2Cc_limit/NABRAND-15854_HF_Refresh_PeakIIConcepts_2025-07_Shot01.jpg)

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=flat&logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Live%20Demo-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-ML%20%2B%20RAG-F7931E?style=flat&logo=scikitlearn&logoColor=white)
![USDA](https://img.shields.io/badge/USDA-Nutrition%20Verification-2E7D32?style=flat)
![Status](https://img.shields.io/badge/status-API--focused%20MVP-blue?style=flat)

AI Meal Planner is a multi-agent meal planning application that estimates calorie needs, recommends meals from user preferences, verifies nutrition, and prepares a practical shopping-list estimate.

The current phase focuses on a reliable FastAPI service, ML-ready agent modules, and a deployed Streamlit experience for testing and demonstration. The React dashboard remains in the repository and will continue to be refined in the next frontend phase once the API contracts and core workflows are stable.

**Live Demo:** https://tuannm3812-ai-meal-planner.streamlit.app/

## 1. Current Delivery Focus

- Build a dependable API foundation for meal generation, calorie prediction, nutrition verification, feedback, and shopping-list estimates
- Deploy and validate the product through Streamlit while the core recommendation workflow matures
- Preserve the React frontend path for the next phase of UX refinement and production interface work

## 2. Features

- Calorie target calculation with a dedicated calorie expenditure agent
- Kaggle-trained calorie expenditure model artifact promoted into the backend workflow
- Local vector RAG meal retrieval for stable meal recommendations without requiring Gemini for base generation
- Allergy, dietary preference, and health-condition filtering before retrieval
- Portion scaling, ingredient substitutions, and structured retrieval metadata
- Nutrition verification through USDA FoodData Central, optional FatSecret lookup, and local fallback estimates
- User feedback capture for likes, ratings, saved meals, and notes
- File-backed user profiles and meal history for early pilots
- Supermarket product mapping with estimated shopping cost and confidence metadata
- Streamlit demo for local testing and deployed product review

## 3. Tech Stack

- Backend: Python, FastAPI, Pydantic, Uvicorn
- ML/RAG: scikit-learn, TF-IDF vector retrieval, optional sentence-transformers + FAISS
- AI: Google Gemini via `google-genai`, reserved for optional final explanation/adaptation
- Nutrition: USDA FoodData Central, optional FatSecret, trusted local fallbacks
- Demo UI: Streamlit
- Frontend: React, Vite, Tailwind CSS, Axios
- Tooling: pytest, GitHub Actions CI, Ruff config, ESLint, npm

## 4. Architecture

```text
User profile + craving
-> CalorieExpenditureAgent predicts daily expenditure
-> MealRecommendationAgent filters constraints and retrieves from local vector RAG
-> Portion scaling and substitution rules adapt the selected meal template
-> Optional Gemini final explanation when ENABLE_GEMINI_ADAPTATION=1
-> NutritionVerificationAgent verifies ingredients through USDA/FatSecret/local references
-> SupermarketAgent maps ingredients to local grocery estimates
-> Streamlit renders the response for testing and demos
```

The meal path is retrieval-first so common cravings continue to work when external AI services are rate limited or disabled.

## 5. Project Structure

```text
ai-meal-planner/
|-- backend/
|   |-- app/
|   |   |-- agents/
|   |   |-- core/
|   |   |-- rag/
|   |   |-- repositories/
|   |   |-- schemas/
|   |   `-- main.py
|   |-- tests/
|   `-- requirements.txt
|-- data/
|   `-- meal_corpus/
|-- database/
|   `-- user_profiles.example.json
|-- docs/
|-- frontend/
|-- models/
|-- notebooks/
|-- streamlit_app/
|   `-- app.py
|-- .env.example
|-- render.yaml
|-- requirements.txt
|-- runtime.txt
`-- README.md
```

See `docs/architecture/system_architecture.md` and `docs/engineering/repo_structure_conventions.md` for deeper design notes.

## 6. Quick Start

### 6.1 Prerequisites

- Python 3.11+
- Optional: Node.js 20+ and npm for the React dashboard
- Optional: Gemini, USDA, and FatSecret API keys for live external integrations

### 6.2 Backend API

Run these commands from the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r backend/requirements.txt
Copy-Item .env.example backend/.env
uvicorn backend.app.main:app --host 127.0.0.1 --port 8010 --reload
```

The API runs at:

```text
http://127.0.0.1:8010
```

Interactive API docs are available at:

```text
http://127.0.0.1:8010/docs
```

### 6.3 Streamlit Demo

For a local self-contained demo:

```powershell
$env:STREAMLIT_DEMO_MODE="1"
streamlit run streamlit_app/app.py
```

For API-client mode with FastAPI running locally:

```powershell
$env:API_BASE_URL="http://127.0.0.1:8010"
streamlit run streamlit_app/app.py
```

The local Streamlit app runs at:

```text
http://localhost:8501
```

The deployed Streamlit Community Cloud demo is available at:

```text
https://tuannm3812-ai-meal-planner.streamlit.app/
```

### 6.4 React Dashboard

The React dashboard is retained for the next frontend refinement phase.

```powershell
cd frontend
npm install
npm run dev
```

Local React development runs at:

```text
http://localhost:5173
```

## 7. Configuration

Create `backend/.env` from `.env.example` and adjust values as needed:

```env
APP_ENV=development
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:8501
GEMINI_API_KEY=
USDA_API_KEY=
FATSECRET_CLIENT_ID=
FATSECRET_CLIENT_SECRET=
CALORIE_MODEL_PATH=models/calorie_expenditure/calorie_expenditure_model.joblib
CALORIE_MODEL_VERSION=hist_gradient_boosting_deep_v0.1.0
MEAL_CORPUS_PATH=data/meal_corpus/meals.json
RAG_BACKEND=auto
ENABLE_GEMINI_ADAPTATION=0
```

`GEMINI_API_KEY`, `USDA_API_KEY`, and FatSecret credentials are optional. The backend includes deterministic fallbacks so the core workflow remains usable without external API keys.

## 8. API Overview

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/` | Basic API status and endpoint links |
| `GET` | `/health` | Service health and external provider configuration status |
| `POST` | `/generate-meal-plan` | Generate a meal plan from craving, location, profile, and dietary constraints |
| `GET` | `/meal-plans/{user_id}` | Return recent meal plans for a user |
| `POST` | `/meal-feedback` | Save likes, ratings, saved-meal state, and notes |
| `GET` | `/meal-feedback/{user_id}` | Return feedback history for a user |
| `GET` | `/saved-meals/{user_id}` | Return saved meals for a user |
| `POST` | `/calorie-expenditure/predict` | Predict daily calorie expenditure and meal calorie budget |

Example meal-generation request:

```json
{
  "user_id": "user_123",
  "craving": "high-protein burger",
  "location": "Earlwood, NSW",
  "health_conditions": ["hypertension"],
  "dietary_preferences": ["high protein", "low sodium"]
}
```

Example calorie-prediction request:

```json
{
  "age": 28,
  "sex": "male",
  "height_cm": 180,
  "weight_kg": 80,
  "activity_multiplier": 1.55,
  "duration_minutes": 30,
  "heart_rate_bpm": 100,
  "body_temp_c": 40,
  "goal": "maintain",
  "health_conditions": ["hypertension"]
}
```

## 9. Development

Run backend tests:

```powershell
python -m pytest -q
```

Run a health smoke test:

```powershell
curl http://127.0.0.1:8010/health
```

Build and lint the React dashboard:

```powershell
cd frontend
npm run lint
npm run build
```

## 10. Model and Retrieval Assets

```text
notebooks/calorie_expenditure_kaggle_training.ipynb
models/calorie_expenditure/calorie_expenditure_model.joblib
models/calorie_expenditure/metrics.json
models/calorie_expenditure/feature_schema.json
data/meal_corpus/meals.json
backend/app/rag/retriever.py
```

The current seed corpus contains 34 curated meal templates. The recommendation flow filters health and allergy conflicts, retrieves from the local vector corpus, applies known substitutions, and scales portions before any optional Gemini step.

Semantic retrieval is prepared but conservative by default. In production, `RAG_BACKEND=auto` keeps TF-IDF for small corpora and moves to sentence embeddings plus FAISS when the corpus reaches the configured activation size.

## 11. Roadmap

- Connect `/generate-meal-plan` more tightly with the latest `/calorie-expenditure/predict` result
- Expand `data/meal_corpus/meals.json` from 34 templates to 75-100 curated templates
- Use saved meals, likes, dislikes, and ratings as ranking features in retrieval
- Move local JSON stores for history, feedback, and profiles to a managed database
- Improve macro-target balancing, serving-size normalization, and ingredient matching
- Continue refining the Streamlit experience while preparing the React dashboard for the next production frontend phase
