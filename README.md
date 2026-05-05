# AI Meal Planner

A multi-agent meal planning prototype that turns a user's craving into a structured meal plan, nutrition summary, and supermarket shopping list.

The project combines a FastAPI backend with a React dashboard. The backend orchestrates specialized agents for meal definition, macro calculation, and grocery mapping. The frontend provides a clean dashboard for submitting a craving and reviewing the generated result.

## Features

- Craving-based meal generation using a meal definition agent
- User context support through a mock profile database
- Nutrition calculation for calories, protein, carbs, and fat
- Supermarket product mapping with estimated shopping cost
- React dashboard with loading, error, and results states
- FastAPI endpoint for the full orchestration chain

## Tech Stack

- Backend: Python, FastAPI, Pydantic, Uvicorn
- AI: Google Gemini via `google-generativeai`
- Frontend: React, Vite, Tailwind CSS, Axios
- Tooling: ESLint, npm

## Project Structure

```text
ai-meal-planner/
├── backend/
│   ├── main.py
│   ├── meal_definition_agent.py
│   ├── nutrition_agent.py
│   └── supermarket_agent.py
├── blueprints/
│   ├── 00_system_architecture.md
│   ├── 01_coding_guidelines.md
│   ├── 02_meal_definition_agent.md
│   ├── 03_nutrition_agent.md
│   ├── 04_supermarket_agent.md
│   └── 05_react_frontend.md
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   ├── package.json
│   └── tailwind.config.js
└── README.md
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
pip install fastapi uvicorn pydantic python-dotenv google-generativeai
```

Create `backend/.env` if you want to use Gemini:

```env
GEMINI_API_KEY=your_api_key_here
```

Run the API:

```bash
python main.py
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

The dashboard runs at:

```text
http://localhost:5173
```

## API

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
  }
}
```

## Development Commands

Frontend:

```bash
cd frontend
npm run lint
npm run build
```

Backend:

```bash
cd backend
python main.py
```

## Notes

- The backend includes mocked nutrition, supermarket, and user profile data for prototyping.
- If Gemini is unavailable or rate limited, the meal definition agent falls back to mock data so local development can continue.
- `backend/.env`, `venv`, `node_modules`, build output, and Python caches are intentionally ignored by Git.

## Roadmap

- Add persistent user profiles and meal history
- Replace mock nutrition data with USDA FoodData Central integration
- Replace mock supermarket mapping with live inventory and store APIs
- Add automated backend tests
- Add deployment configuration for frontend and backend
