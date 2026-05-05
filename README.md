# AI Meal Planner

A multi-agent meal planning app that turns a user's craving into a structured meal plan, nutrition summary, and supermarket shopping list.

The project combines a FastAPI backend with a React dashboard. The backend orchestrates specialized agents for meal definition, macro calculation, and grocery mapping. The frontend provides a clean dashboard for submitting a craving and reviewing the generated result.

## Features

- Craving-based meal generation using a meal definition agent
- User context support through file-backed profile data with a default fallback
- Nutrition calculation with optional USDA FoodData Central lookup and local estimates
- Supermarket product mapping with estimated shopping cost and confidence metadata
- React dashboard with loading, error, and results states
- FastAPI endpoints for generation, health checks, and user meal history

## Tech Stack

- Backend: Python, FastAPI, Pydantic, Uvicorn
- AI: Google Gemini via `google-genai`
- Frontend: React, Vite, Tailwind CSS, Axios
- Tooling: ESLint, npm

## Project Structure

```text
ai-meal-planner/
|-- backend/
|   |-- config.py
|   |-- main.py
|   |-- meal_definition_agent.py
|   |-- nutrition_agent.py
|   |-- requirements.txt
|   |-- storage.py
|   `-- supermarket_agent.py
|-- blueprints/
|-- database/
|   `-- user_profiles.example.json
|-- frontend/
|   |-- src/
|   |-- package.json
|   `-- tailwind.config.js
`-- README.md
```

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+
- npm
- Optional: a Gemini API key for live AI generation

### Backend Setup

From the project root:

```bash
cd backend
python -m venv ../venv
../venv/Scripts/activate
pip install -r requirements.txt
```

Create `backend/.env` from the example file:

```env
APP_ENV=development
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
GEMINI_API_KEY=your_gemini_api_key_here
USDA_API_KEY=optional_usda_api_key_here
```

Run the API:

```bash
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

### Frontend Setup

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

For a deployed backend, set the API base URL before building:

```env
VITE_API_URL=https://your-backend.example.com
```

The dashboard runs at:

```text
http://localhost:5173
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

## Development Commands

Frontend:

```bash
cd frontend
npm run lint
npm run build
```

Backend:

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Smoke test:

```bash
curl http://localhost:8000/health
```

## Notes

- The backend includes deterministic fallbacks so the workflow stays usable when optional external APIs are unavailable.
- Nutrition and grocery results include source and confidence metadata for safer user-facing display.
- Generated meal history is saved to `database/meal_history.json`, which is intentionally ignored by Git.
- `backend/.env`, `venv`, `node_modules`, build output, and Python caches are intentionally ignored by Git.

## Roadmap

- Move meal history and user profiles to a managed database
- Expand USDA FoodData Central integration and serving-size normalization
- Replace local supermarket estimates with live inventory and store APIs
- Add automated backend tests
- Add deployment configuration for frontend and backend
- Improve dashboard UI, result explainability, and meal history views
