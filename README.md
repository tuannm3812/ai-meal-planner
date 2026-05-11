# AI Meal Planner

A backend-first, multi-agent meal planning app that predicts calorie needs, recommends meals from user preferences, and verifies nutrition with authoritative food data.

The project combines a FastAPI backend, ML-ready agent modules, and a lightweight path to Streamlit demos. React remains in the repo for later UI refinement, but backend contracts come first.

## Features

- Calorie target calculation with a dedicated calorie expenditure agent
- Promoted compact Kaggle-trained calorie expenditure model artifact
- Preference-aware meal generation using typed ingredient outputs
- Planned RAG layer for retrieving known meals before LLM adaptation
- Nutrition calculation with optional USDA and FatSecret lookup plus local estimates
- User context support through file-backed profile data with a default fallback
- Supermarket product mapping with estimated shopping cost and confidence metadata
- FastAPI endpoints for generation, health checks, and user meal history
- React dashboard retained for later frontend refinement

## Tech Stack

- Backend: Python, FastAPI, Pydantic, Uvicorn
- ML: scikit-learn-compatible training notebook for Kaggle
- AI: Google Gemini via `google-genai`
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
CALORIE_MODEL_PATH=models/calorie_expenditure/calorie_expenditure_model.joblib
CALORIE_MODEL_VERSION=hist_gradient_boosting_deep_v0.1.0
```

Run the API from the project root:

```powershell
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

The backend runs at:

```text
http://localhost:8000
```

Interactive API docs are available at:

```text
http://localhost:8000/docs
```

### Streamlit Demo

With the backend running in one terminal, start the Streamlit demo in another terminal:

```powershell
.\.venv\Scripts\Activate.ps1
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

Recommended GitHub repository metadata:

```text
Name: ai-meal-planner
Description: Backend-first AI meal planner with calorie expenditure prediction, meal generation, and nutrition verification.
```

The Streamlit sidebar includes an optional Gemini API key field for testing meal generation. In production, prefer configuring `GEMINI_API_KEY` on the backend environment instead of entering it in the UI.

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

### `GET /health`

Returns API status plus whether optional external services are configured.

### `POST /generate-meal-plan`

Request body:

```json
{
  "user_id": "user_123",
  "craving": "high-protein burger",
  "location": "Earlwood, NSW"
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
          "item_name": "ground turkey (93% lean)",
          "base_quantity_grams": 150
        }
      ]
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

## Notes

- The backend includes deterministic fallbacks so the workflow stays usable when optional external APIs or model artifacts are unavailable.
- The promoted calorie expenditure model was trained with scikit-learn 1.6.1; keep that version pinned for compatible artifact loading.
- Nutrition and grocery results include source and confidence metadata for safer user-facing display.
- Nutrition provider order is USDA, then FatSecret, then local reference/category estimates.
- FatSecret may require your server IP address to be allowed in the FatSecret developer console before food search calls succeed.
- Generated meal history is saved to `database/meal_history.json`, which is intentionally ignored by Git.
- `backend/.env`, `venv`, `node_modules`, build output, and Python caches are intentionally ignored by Git.

## Roadmap

- Integrate calorie expenditure output directly into the meal recommendation orchestration
- Split the current meal definition flow into Calorie Expenditure, Meal Recommendation, and Nutrition Verification agents
- Add RAG over a curated meal corpus to reduce free-form generation dependency
- Add a Streamlit app for backend-first demos
- Move meal history and user profiles to a managed database
- Expand USDA FoodData Central integration and serving-size normalization
- Replace local supermarket estimates with live inventory and store APIs
- Add automated backend tests
- Add deployment configuration for frontend and backend
- Improve dashboard UI, result explainability, and meal history views
