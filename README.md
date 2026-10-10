# AI Meal Planner

![AI Meal Planner hero](https://assets.epicurious.com/photos/689523e500efe724a5ef8bb5/16:9/w_2560%2Cc_limit/NABRAND-15854_HF_Refresh_PeakIIConcepts_2025-07_Shot01.jpg)

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=flat&logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Live%20Demo-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-ML%20%2B%20RAG-F7931E?style=flat&logo=scikitlearn&logoColor=white)
![USDA](https://img.shields.io/badge/USDA-Nutrition%20Verification-2E7D32?style=flat)
![Status](https://img.shields.io/badge/status-API--focused%20MVP-blue?style=flat)

AI Meal Planner is a multi-agent meal planning application that estimates calorie needs, recommends meals from user preferences, verifies nutrition, and prepares a practical shopping-list estimate.

The current phase focuses on a reliable FastAPI service, ML-ready agent modules, and two client experiences for testing and demonstration: a deployed Streamlit app and a React dashboard, both covering meal planning, calorie prediction, and history/saved-meal review.

**Live Demo:** https://tuannm3812-ai-meal-planner.streamlit.app/

## 1. Current Delivery Focus

- Build a dependable API foundation for meal generation, calorie prediction, nutrition verification, feedback, and shopping-list estimates
- Deploy and validate the product through Streamlit while the core recommendation workflow matures
- Streamlit and React now cover the same core workflow (meal plan, calorie prediction, history); harden the React dashboard toward a production interface next

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
- Cached USDA/FatSecret nutrition lookups with automatic per-provider cooldown after repeated failures, so a slow or misconfigured provider degrades gracefully instead of stalling every request
- Streamlit demo and React dashboard, both covering meal plan generation, calorie prediction, and meal/feedback history

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

As of 2026-09-10 the calorie prediction step runs only via `/calorie-expenditure/predict`; `/generate-meal-plan` does not yet consume its budget — see [`docs/2_architecture.md`](docs/2_architecture.md) and [`docs/4_next_steps.md`](docs/4_next_steps.md) §1.1.

The meal path is retrieval-first so common cravings continue to work when external AI services are rate limited or disabled.

## 5. Project Structure

```text
ai-meal-planner/
|-- AGENTS.md
|-- CLAUDE.md
|-- backend/
|   |-- app/
|   |   |-- agents/
|   |   |-- core/
|   |   |-- ml/            (empty scaffolding)
|   |   |-- rag/
|   |   |-- repositories/
|   |   |-- schemas/
|   |   |-- services/      (empty scaffolding)
|   |   `-- main.py
|   |-- tests/
|   `-- requirements.txt
|-- data/
|   `-- meal_corpus/
|-- database/
|   `-- user_profiles.example.json
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
|-- models/
|-- notebooks/
|-- streamlit_app/
|   `-- app.py
|-- .env.example
|-- render.yaml
|-- requirements.txt
|-- runtime.txt
|-- uv.lock
`-- README.md
```

See [`docs/2_architecture.md`](docs/2_architecture.md) and [`docs/0_coding_standards.md`](docs/0_coding_standards.md) for deeper design notes.

## 6. Quick Start

### 6.1 Prerequisites

- [uv](https://docs.astral.sh/uv/) — manages the Python version and dependencies
- Optional: Node.js 20+ and npm for the React dashboard
- Optional: Gemini, USDA, and FatSecret API keys for live external integrations

`uv` installs and pins Python 3.11 itself, so no system Python is required.

### 6.2 Backend API

Run these commands from the project root. They work identically on macOS, Linux
and Windows.

```bash
uv sync --all-groups
cp backend/.env.example backend/.env
uv run uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

On Windows PowerShell, substitute the copy step:

```powershell
Copy-Item backend/.env.example backend/.env
```

The API runs at `http://127.0.0.1:8000`, with interactive docs at
`http://127.0.0.1:8000/docs`.

### 6.3 Streamlit Demo

For a local self-contained demo:

```bash
STREAMLIT_DEMO_MODE=1 uv run streamlit run streamlit_app/app.py
```

On Windows PowerShell:

```powershell
$env:STREAMLIT_DEMO_MODE="1"
uv run streamlit run streamlit_app/app.py
```

For API-client mode with FastAPI running locally:

```bash
API_BASE_URL=http://127.0.0.1:8000 uv run streamlit run streamlit_app/app.py
```

On Windows PowerShell:

```powershell
$env:API_BASE_URL="http://127.0.0.1:8000"
uv run streamlit run streamlit_app/app.py
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

The React dashboard covers the same three workflows as the Streamlit app: meal plan generation, calorie prediction, and meal/feedback history, with the FastAPI backend as its only dependency (no demo mode).

If the backend is not reachable at `localhost:8000`, copy `frontend/.env.example`
to `frontend/.env.local` and adjust it before starting the dev server.

```bash
cd frontend
npm install
npm run dev
```

Local React development runs at:

```text
http://localhost:5173
```

### 6.5 Docker

One image runs the FastAPI backend. Compose runs the same image a second time as the Streamlit client in API mode, pointed at the backend:

```bash
docker compose up --build --wait
```

This serves the API at `http://localhost:8000` (`/health`, `/docs`) and Streamlit at `http://localhost:8501`.

- **Dependencies.** The image installs from `uv.lock`, the single source behind the generated requirements files, so it resolves exactly the versions CI tests. Test tooling, the frontend, notebooks and all local data are left out. `.dockerignore` is an allowlist.
- **No persisted history.** History lives inside the container and disappears when the container is removed. That is stateless v1; no volume is mounted, and no migration or data import runs.
- **Configuration.** `API_KEYS`, provider keys and `MEAL_PLANNER_API_KEY` are read from your shell or a `.env` file next to `compose.yaml`. Without `API_KEYS` the API runs in open local mode (see [8.1](#81-security)).
- **Restart versus redeploy.** Restarting the same container keeps its history, because its writable layer survives. A redeploy creates a new container, which starts empty. That is what "stateless v1" means here.
- **Hosted rehearsal.** `compose.hosted.yaml` runs two `HOSTED_MODE` instances behind one nginx URL, and `scripts/hosted_smoke.sh` checks that both refuse history. It rehearses the multi-instance shape and is not a deployment.
- **Smoke test.** `scripts/container_smoke.sh` builds the stack and checks it, the same way CI's `container` job does. It runs as its own compose project, on free ports and with its own image tag, so it never touches a stack you already have running. It also pins open, keyless, offline settings and ignores your `.env`. It checks `/health`, that history starts empty, that no secrets are baked in, that a meal plan generates offline, and that Streamlit is up.

## 7. Configuration

Create `backend/.env` from `backend/.env.example` and adjust values as needed:

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
STORAGE_BACKEND=sqlite
REQUIRE_VERIFIED_NUTRITION=0
API_KEYS=
RATE_LIMIT_PER_MINUTE=60
```

`REQUIRE_VERIFIED_NUTRITION=1` makes a meal fail with `502` (code `unverified_required`) when any ingredient's nutrition could only be estimated. It is off by default so the keyless demo keeps producing plans. `API_KEYS` and `RATE_LIMIT_PER_MINUTE` are described in [8.1 Security](#81-security).

**Existing SQLite databases.** A database created before G4 has no `client_id` column, and there are no migrations, so the API refuses to start against one and names the file. Under stateless v1, delete `database/ai_meal_planner.db` and restart; it is recreated empty.

`GEMINI_API_KEY`, `USDA_API_KEY`, and FatSecret credentials are optional. The backend includes deterministic fallbacks so the core workflow remains usable without external API keys.

`HOSTED_MODE=true` marks a hosted, multi-instance deployment. Each instance has its own SQLite file, so history written on one would be invisible on the others. Hosted mode therefore refuses the three history reads and `POST /meal-feedback` with `501 history_disabled_stateless`, and it stores no generated plans. Meal planning and calorie prediction keep working, `/health` stays public and reports `hosted_mode`, and both clients hide history and feedback when it is set. It is off by default.

`STORAGE_BACKEND` selects where meal history and feedback are persisted. `sqlite` is the default and starts from an empty database at `database/ai_meal_planner.db`; existing JSON records are imported once with `uv run python scripts/migrate_json_to_sqlite.py`. That script is not idempotent, so running it twice duplicates every record. `STORAGE_BACKEND=json` keeps the previous file-backed behaviour, reading and writing `database/*.json` directly.

## 8. API Overview

| Method | Endpoint | Scope | Purpose |
| --- | --- | --- | --- |
| `GET` | `/` | public | Basic API status and endpoint links |
| `GET` | `/health` | public | Service health and external provider configuration status |
| `POST` | `/generate-meal-plan` | `plans:write` | Generate a meal plan from craving, location, profile, and dietary constraints |
| `GET` | `/meal-plans/{user_id}` | `history:read` | Return recent meal plans for a user |
| `POST` | `/meal-feedback` | `feedback:write` | Save likes, ratings, saved-meal state, and notes for a plan you generated |
| `GET` | `/meal-feedback/{user_id}` | `history:read` | Return feedback history for a user |
| `GET` | `/saved-meals/{user_id}` | `history:read` | Return saved meals for a user |
| `POST` | `/calorie-expenditure/predict` | `plans:write` | Predict daily calorie expenditure and meal calorie budget |

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

### 8.1 Security

**Who the keys identify.** API keys identify trusted client *applications*, not end users. Each key record carries a stable `client_id`, and every stored meal plan and feedback record belongs to that `client_id`. A `user_id` is only an identifier within one client's namespace, so guessing another `user_id` never reaches another client's data. Feedback must reference a `request_id` the same client generated; anything else is `404 meal_not_found`, indistinguishable from an id that never existed.

**Configuring keys.** `API_KEYS` is a JSON list. An empty list (`[]`) means no keys: open local mode in development, refused in production. Only SHA-256 hashes are configured, so a leaked environment dump does not leak usable keys:

```bash
python -c "import hashlib,sys;print(hashlib.sha256(sys.argv[1].encode()).hexdigest())" 'the-raw-key'
```

```env
API_KEYS=[{"client_id": "partner-app", "key_sha256": "<hex digest>", "scopes": ["plans:write", "feedback:write", "history:read"]}]
```

Send the raw key as `X-API-Key`. The scopes are `plans:write`, `feedback:write` and `history:read`; there is deliberately no admin scope. A malformed `API_KEYS` stops the API at startup rather than running half-configured.

**Rotation and revocation.** To rotate, add a record with a new key hash and the **same** `client_id`, deploy, move the client to the new key, then remove the old record and deploy again. The namespace is unchanged throughout. To revoke, remove the record and redeploy: every instance reads `API_KEYS` at startup, so after rollout no instance accepts the old key.

**Rate limit.** `RATE_LIMIT_PER_MINUTE` (default 60) is a fixed one-minute window per `client_id`, held **in each instance's memory**. With N instances a client can make up to N times the limit. It is a per-instance safeguard, not an account-wide quota. Exceeding it returns `429 rate_limited` with `Retry-After`.

**Open local mode.** With `API_KEYS` empty the API runs unauthenticated under a single `local` namespace and logs a warning at startup; this is how the React dashboard works in development, since a key placed in a `VITE_*` variable would be baked into the public bundle. `APP_ENV=production` with no keys refuses to start, so a hosted deployment cannot be open by accident. Calling a keyed API from the React dashboard is out of scope for v1.

**Clients.** The Streamlit app in API mode sends `MEAL_PLANNER_API_KEY` from its server-side secrets; it is never shown in the page. The key is bound to the operator-set `API_BASE_URL`: it is sent only when a request's scheme, host and port match that secret, so a visitor who edits the sidebar's Base URL reaches their URL without the key. Backend calls never follow redirects, because a custom `X-API-Key` header would otherwise follow a 30x to another host. The public Streamlit demo runs the backend in-process and holds no key. Provider credentials (Gemini, USDA, FatSecret) are server-managed only: the former per-request `X-Gemini-Api-Key` pass-through has been removed.

**Errors.** `401 missing_or_invalid_api_key`, `403 insufficient_scope`, `404 meal_not_found`, `429 rate_limited`, and `501 history_disabled_stateless` in hosted mode. Bodies carry a stable `code` and a client-safe `detail`; internal detail goes to the server log only.

**Upgrade path.** Per-user identity (OAuth/OIDC tokens) is the documented next step if end users ever call the API directly; see `docs/3_decisions.md` DEC-7.

## 9. Development

Run the backend checks — the same gates CI enforces:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

Build and lint the React dashboard:

```bash
cd frontend
npm ci
npm run lint
npm run build
```

Health smoke test, with the backend running:

```bash
curl http://127.0.0.1:8000/health
```

**Dependencies:** `pyproject.toml` is the only file to edit by hand. After
changing it, run `uv lock` and regenerate the export that Render installs from:

```bash
uv export --no-dev --no-hashes --no-emit-project --format requirements.txt -o backend/requirements.txt
```

CI fails if `backend/requirements.txt` drifts from `uv.lock`.

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

The full prioritised backlog, including the deliberate gaps, is in
[`docs/4_next_steps.md`](docs/4_next_steps.md). Highlights:

- Consume the budget from `/calorie-expenditure/predict` in `/generate-meal-plan`
- Expand `data/meal_corpus/meals.json` from 34 templates to 75-100 curated templates
- Use saved meals, likes, dislikes, and ratings as ranking features in retrieval
- Move local JSON stores for history, feedback, and profiles to a managed database
- Improve macro-target balancing, serving-size normalization, and ingredient matching
- Add authentication and persistent accounts to the React dashboard as it moves toward a production interface
