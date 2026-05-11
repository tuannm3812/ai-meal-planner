# AI Meal Planner

![AI Meal Planner hero](https://assets.epicurious.com/photos/689523e500efe724a5ef8bb5/16:9/w_2560%2Cc_limit/NABRAND-15854_HF_Refresh_PeakIIConcepts_2025-07_Shot01.jpg)

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Demo-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-ML%20%2B%20RAG-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white)
![USDA](https://img.shields.io/badge/USDA-Nutrition%20Verification-2E7D32?style=for-the-badge)
![Status](https://img.shields.io/badge/status-backend--first%20MVP-blue?style=for-the-badge)

A backend-first, multi-agent meal planning app that predicts calorie needs, recommends meals from user preferences, and verifies nutrition with authoritative food data.

The project combines a FastAPI backend, ML-ready agent modules, and a lightweight path to Streamlit demos. React remains in the repo for later UI refinement, but backend contracts come first.

## Features

- Calorie target calculation with a dedicated calorie expenditure agent
- Promoted compact Kaggle-trained calorie expenditure model artifact
- Local vector RAG meal retrieval to reduce Gemini calls and handle rate limits
- Preference-aware meal generation using typed ingredient outputs
- Nutrition calculation with optional USDA and FatSecret lookup plus local estimates
- User context support through file-backed profile data with a default fallback
- Supermarket product mapping with estimated shopping cost and confidence metadata
- FastAPI endpoints for generation, health checks, and user meal history
- Streamlit API client for backend-first testing and demos
- React dashboard retained for later frontend refinement

## Tech Stack

- Backend: Python, FastAPI, Pydantic, Uvicorn
- ML/RAG: scikit-learn, TF-IDF vector retrieval, Kaggle-trained calorie model
- AI: Google Gemini via `google-genai`, used only when retrieval cannot satisfy the meal request
- Nutrition: USDA FoodData Central, optional FatSecret, trusted local fallbacks
- Demo UI: Streamlit
- Frontend: React, Vite, Tailwind CSS, Axios
- Tooling: Ruff, pytest, ESLint, npm

## Project Structure

```text
ai-meal-planner/
|-- backend/
|   |-- app/
|   |   |-- agents/
|   |   |-- core/
|   |   |-- ml/
|   |   |-- rag/
|   |   |-- repositories/
|   |   |-- schemas/
|   |   |-- services/
|   |   `-- main.py
|   |-- tests/
|   |-- main.py
|   `-- requirements.txt
|-- data/
|   `-- meal_corpus/
|-- docs/
|-- models/
|-- notebooks/
|-- database/
|   `-- user_profiles.example.json
|-- streamlit_app/
|   `-- app.py
|-- frontend/
|   |-- src/
|   |-- package.json
|   `-- tailwind.config.js
|-- .env.example
|-- requirements.txt
|-- pyproject.toml
`-- README.md
```

See `docs/architecture/system_architecture.md` and `docs/engineering/repo_structure_conventions.md` for deeper design notes.

## Current Architecture

```text
User profile + craving
-> CalorieExpenditureAgent predicts daily expenditure
-> MealRecommendationAgent retrieves a meal from local vector RAG
-> Gemini is used only if retrieval cannot find a strong match
-> NutritionVerificationAgent verifies ingredients through USDA/FatSecret/local references
-> SupermarketAgent maps ingredients to local grocery estimates
-> Streamlit renders the response for testing
```

The meal path is retrieval-first so common cravings work even when Gemini is rate limited.

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+
- npm
- Optional: a Gemini API key for live AI generation
- Optional: a USDA FoodData Central API key for live nutrition lookup

### Backend Setup

Run these commands from the project root in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r backend/requirements.txt
```

If activation fails with "not recognized", the `.venv` folder does not exist in the project root yet. Run `python -m venv .venv` first, then activate it again:

```powershell
Test-Path .\.venv\Scripts\Activate.ps1
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation scripts, allow them for the current shell session:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Create `backend/.env` from `.env.example`:

```powershell
Copy-Item .env.example backend/.env
```

Then edit `backend/.env` as needed:

```env
APP_ENV=development
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:8501
GEMINI_API_KEY=
USDA_API_KEY=
FATSECRET_CLIENT_ID=
FATSECRET_CLIENT_SECRET=
MAPS_API_KEY=
INVENTORY_API_KEY=
CALORIE_MODEL_PATH=models/calorie_expenditure/calorie_expenditure_model.joblib
CALORIE_MODEL_VERSION=hist_gradient_boosting_deep_v0.1.0
MEAL_CORPUS_PATH=data/meal_corpus/meals.json
```

`MAPS_API_KEY` and `INVENTORY_API_KEY` are placeholders for later live grocery integrations. You can leave them blank; the current supermarket agent uses local fallback store and price estimates.

Restart the backend after changing `backend/.env`; FastAPI reads those values at startup.

Run the API from the project root:

```powershell
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

The backend root endpoint runs at:

```text
http://localhost:8000
```

If you open the root URL in a browser, you should see a small JSON status payload. Interactive API docs are available at:

```text
http://localhost:8000/docs
```

### Streamlit Demo

With the backend running in one terminal, start the Streamlit demo in another terminal:

```powershell
.\.venv\Scripts\Activate.ps1
streamlit run streamlit_app/app.py
```

If you are using your global Python environment instead of `.venv`, install the dependencies first and run Streamlit directly:

```powershell
pip install -r requirements.txt
streamlit run streamlit_app/app.py
```

The Streamlit demo runs at:

```text
http://localhost:8501
```

To point Streamlit at a deployed API:

```powershell
$env:API_BASE_URL="https://your-backend.example.com"
streamlit run streamlit_app/app.py
```

### Streamlit Cloud Deployment

Use these values in Streamlit Community Cloud:

```text
Repository: tuannm3812/ai-meal-planner
Branch: main
Main file path: streamlit_app/app.py
App URL: choose an available slug, for example tuannm-ai-meal-planner
```

Use a forward slash in `streamlit_app/app.py`. A Windows backslash path such as `streamlit_app\app.py` can show as missing in Streamlit Cloud.

Add secrets in Streamlit Cloud under app settings:

```toml
API_BASE_URL = "https://your-fastapi-backend-url"
GEMINI_API_KEY = "optional-gemini-key"
```

The current Streamlit app is an API client. For deployed testing, the FastAPI backend must also be running somewhere reachable by `API_BASE_URL`.

Local Streamlit can also read environment variables or `.streamlit/secrets.toml`. The app does not require a secrets file; missing secrets fall back to `http://localhost:8000`.

### Public FastAPI Deployment

The repo includes `render.yaml` for a first public FastAPI deployment on Render.

Render setup:

```text
Repository: tuannm3812/ai-meal-planner
Service type: Web Service
Build command: pip install -r backend/requirements.txt
Start command: uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
Health check path: /health
```

Required Render environment variables:

```text
APP_ENV=production
ALLOWED_ORIGINS=https://tuannm3812-ai-meal-planner.streamlit.app,http://localhost:8501,http://127.0.0.1:8501
USDA_API_KEY=your-usda-key
RAG_BACKEND=auto
ENABLE_GEMINI_ADAPTATION=0
```

Optional Render environment variables:

```text
GEMINI_API_KEY=only-if-final-explanations-are-enabled
FATSECRET_CLIENT_ID=optional
FATSECRET_CLIENT_SECRET=optional
```

After Render gives you a public URL, verify:

```text
https://your-render-service.onrender.com/health
```

Then set Streamlit Cloud secret:

```toml
API_BASE_URL = "https://your-render-service.onrender.com"
```

Deployment dependency notes:

- `runtime.txt` pins Streamlit Cloud to Python 3.11.
- `pyproject.toml` includes minimal Poetry metadata so Streamlit Cloud does not fail dependency detection.
- `requirements.txt` still delegates to `backend/requirements.txt` for local and uv-based installs.
- Semantic RAG dependencies are optional; install them only when you are ready to run the FAISS embedding backend.

Recommended GitHub repository metadata:

```text
Name: ai-meal-planner
Description: Backend-first AI meal planner with calorie expenditure prediction, meal generation, and nutrition verification.
```

The Streamlit sidebar includes an optional Gemini API key field for testing meal generation. In production, prefer configuring `GEMINI_API_KEY` on the backend environment instead of entering it in the UI.

### User Feedback

The backend supports lightweight feedback signals that can later train preference-aware retrieval:

```text
POST /meal-feedback
GET /meal-feedback/{user_id}
GET /saved-meals/{user_id}
```

Feedback captures `liked`, `rating`, `saved`, and optional notes. Local feedback is stored in `database/meal_feedback.json`, which is ignored by Git.

### Frontend Setup

In another terminal:

```powershell
cd frontend
npm install
npm run dev
```

The dashboard runs at:

```text
http://localhost:5173
```

For a deployed backend, set the API base URL before building:

```powershell
$env:VITE_API_URL="https://your-backend.example.com"
npm run build
```

Or create a local frontend env file:

```text
VITE_API_URL=https://your-backend.example.com
```

## API

### `GET /`

Returns a small API status payload plus useful endpoint links. This exists so opening `http://localhost:8000` in a browser does not show a 404.

### `GET /health`

Returns API status plus whether optional external services are configured.

### `POST /generate-meal-plan`

Request body:

```json
{
  "user_id": "user_123",
  "craving": "high-protein burger",
  "location": "Earlwood, NSW",
  "health_conditions": ["hypertension"],
  "dietary_preferences": ["high protein", "low sodium"]
}
```

Response shape:

```json
{
  "status": "success",
  "request_id": "2b4b7ac8-4c4a-4d21-aebd-4a7dc9c85854",
  "generated_at": "2026-05-05T00:00:00+00:00",
  "meal_plan": {
    "user_context": {
      "caloric_target": 2848,
      "dietary_restrictions": ["dairy-free", "high-protein"]
    },
    "meal_definition": {
      "craving_input": "high-protein burger",
      "structured_meal_name": "API Rate Limited - Fallback Turkey Burger",
      "ingredients": [
        {
          "item_name": "lean turkey mince",
          "base_quantity_grams": 160
        }
      ]
    },
    "metadata": {
      "agent_name": "MealRecommendationAgent",
      "source": "local_vector_rag_meal_corpus",
      "confidence": 0.72,
      "warnings": []
    }
  },
  "nutrition": {
    "ingredients_macros": [],
    "total_calories": 0,
    "total_protein": 0,
    "total_carbs": 0,
    "total_fat": 0
  },
  "shopping_list": {
    "store_details": {
      "store_name": "Coles Supermarket",
      "address": "Earlwood, NSW 2206"
    },
    "shopping_list": [],
    "total_estimated_cost": 0
  },
  "request": {
    "user_id": "user_123",
    "craving": "high-protein burger",
    "location": "Earlwood, NSW"
  }
}
```

### `GET /meal-plans/{user_id}`

Returns the latest saved meal plan generations for a user. The local JSON history file is intended for early production pilots and can be replaced with Postgres, Firestore, or another managed store later.

### `POST /calorie-expenditure/predict`

Request body:

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

Returns estimated daily expenditure, meal calorie budget, model version, confidence, and health-context warnings. The trained model predicts exercise calories from `duration_minutes`, `heart_rate_bpm`, and `body_temp_c`; the agent adds that to a BMR-based daily estimate.

## Development Commands

Run backend commands from the project root with the Python venv activated.

### Backend

```powershell
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### Backend Tests

```powershell
python -m pytest -q
```

### Health Smoke Test

```powershell
curl http://localhost:8000/health
```

Browser checks:

```text
http://localhost:8000          # API root status payload
http://localhost:8000/docs     # Interactive Swagger docs
http://localhost:8000/health   # Service health JSON
```

### Calorie Prediction Smoke Test

```powershell
$body = @{
  age = 28
  sex = "male"
  height_cm = 180
  weight_kg = 80
  activity_multiplier = 1.55
  duration_minutes = 30
  heart_rate_bpm = 100
  body_temp_c = 40
  goal = "maintain"
  health_conditions = @()
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri http://localhost:8000/calorie-expenditure/predict `
  -Method Post `
  -ContentType "application/json" `
  -Body $body
```

Expected shape:

```json
{
  "estimated_daily_expenditure_kcal": 2924.7,
  "meal_calorie_budget_kcal": 2924.7,
  "model_version": "hist_gradient_boosting_deep_v0.1.0",
  "confidence": 0.82,
  "warnings": []
}
```

The exact calorie value can vary slightly by dependency version, but the response should use the trained model version rather than the fallback model.

### Streamlit

```powershell
streamlit run streamlit_app/app.py
```

### Frontend

```powershell
cd frontend
npm run lint
npm run build
```

### Kaggle Training Notebook and Promoted Model

```text
notebooks/calorie_expenditure_kaggle_training.ipynb
models/calorie_expenditure/calorie_expenditure_model.joblib
models/calorie_expenditure/metrics.json
models/calorie_expenditure/feature_schema.json
```

### Meal Vector RAG Corpus

```text
data/meal_corpus/meals.json
backend/app/rag/meal_corpus.py
backend/app/rag/retriever.py
```

The current seed corpus contains 34 curated meal templates. The meal recommendation flow filters health/allergy conflicts, retrieves from the local vector corpus, applies known substitutions, and scales portions before any optional Gemini step. If retrieval finds a strong match, the API returns a typed meal plan with:

```text
metadata.source = local_vector_rag_meal_corpus
```

RAG responses also include a structured `retrieval` block with the selected meal id, score, matched terms, retriever version, substitutions, and top candidates. Portion scaling metadata is returned in `portion_scaling`.

Gemini is no longer used to create the base meal. It is reserved for optional final explanation/adaptation with `ENABLE_GEMINI_ADAPTATION=1`.

Semantic retrieval is prepared but conservative by default:

```powershell
pip install ".[semantic-rag]"
$env:RAG_BACKEND="sentence-transformers"
$env:RAG_EMBEDDING_ACTIVATION_SIZE="30"
uvicorn backend.app.main:app --reload
```

In production, keep `RAG_BACKEND=auto`. Auto mode keeps TF-IDF for small corpora and moves to local sentence embeddings plus FAISS when the corpus reaches `RAG_EMBEDDING_ACTIVATION_SIZE`, which defaults to `50`.

### Activity Multiplier

The calorie endpoint uses an activity multiplier to estimate total daily energy expenditure from BMR:

```text
1.20  Sedentary
1.375 Light activity
1.55  Moderate activity
1.725 Very active
1.90  Extra active
```

In Streamlit, choose a plain-language activity level. The numeric multiplier is available under advanced settings.

## Notes

- The backend includes deterministic fallbacks so the workflow stays usable when optional external APIs or model artifacts are unavailable.
- Meal generation is retrieval-first. The local vector RAG corpus reduces Gemini usage and makes common cravings work during API quota limits.
- The promoted calorie expenditure model was trained with scikit-learn 1.6.1; keep that version pinned for compatible artifact loading.
- Nutrition and grocery results include source and confidence metadata for safer user-facing display.
- Nutrition provider order is USDA, then FatSecret, then local reference/category estimates.
- FatSecret may require your server IP address to be allowed in the FatSecret developer console before food search calls succeed.
- Generated meal history is saved to `database/meal_history.json`, which is intentionally ignored by Git.
- `backend/.env`, `venv`, `node_modules`, build output, and Python caches are intentionally ignored by Git.

## Roadmap

- Integrate calorie expenditure output directly into the meal recommendation orchestration
- Expand the meal corpus from the current seed set to a normalized recipe dataset
- Use saved meals and ratings to personalize retrieval ranking
- Add macro-target balancing on top of current calorie portion scaling
- Expand optional LLM final explanation after retrieval
- Move meal history and user profiles to a managed database
- Expand USDA FoodData Central integration and serving-size normalization
- Replace local supermarket estimates with live inventory and store APIs
- Add persistent production storage for feedback, history, and user profiles
- Improve dashboard UI, result explainability, and meal history views
