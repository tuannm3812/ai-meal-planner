# Phase 1 — Backend Architecture Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `/generate-meal-plan` actually use the trained calorie model, put a real orchestrator behind it, and give the API testable seams and enforced response contracts.

**Architecture:** A new `services/meal_planning_service.py` becomes the single orchestrator: it calls `CalorieExpenditureAgent`, feeds the resulting budget to `MealRecommendationAgent`, verifies nutrition, reconciles the two calorie figures once if they disagree, and maps ingredients to a shopping list. `main.py` shrinks to app construction plus router registration, with agents built in a `lifespan` handler and injected via `Depends()` so endpoints become testable. Reference data tables move out of agent methods into `data/reference/*.json`.

**Tech Stack:** Python 3.11/3.12, FastAPI, Pydantic v2, pytest, uv, ruff.

**Spec:** `docs/superpowers/specs/2026-09-10-refactor-and-standards-alignment-design.md` §6
**Branches from:** `refactor/phase-0-foundation` (PR #1, not yet merged). PR targets that branch.

## Global Constraints

- **Baseline: 19 passing tests must never drop.** Run `uv run pytest` — **never** `uv run pytest -q`; `pyproject.toml` sets `addopts = "-q"` and a second `-q` becomes `-qq`, hiding the summary. New tests add to the count; report the new number each task.
- **Never `git add -A`.** Run `git status --short`, review every path, stage explicitly. Master standard §10.1.
- Commit format `<type>(<scope>): <imperative summary>`. **The `(scope)` is mandatory.** Every body ends with `Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>`.
- **Do not modify** `.gitignore`, `uv.lock`, `backend/requirements.txt`, `notebooks/**`, or `.github/workflows/ci.yml`. If a task genuinely needs a dependency, stop and report — adding one requires `uv lock` plus a re-export.
- `scikit-learn==1.6.1` stays pinned; the shipped model artifact depends on it.
- Ruff must stay clean: `uv run ruff check .` and `uv run ruff format --check .`.
- **Google-style docstrings** on every public class and function you add or substantially edit (master standard §3).
- **No new dependencies.** `pydantic-settings` is NOT installed and is Phase 2's problem, not this phase's.
- Work on branch `refactor/phase-1-backend-architecture`. Do not push or open PRs; the controller handles that.
- **When you change a function's signature, grep the WHOLE repo for callers, not just
  `backend/`.** `streamlit_app/app.py` calls the agents directly and has no test coverage, so a
  missed caller there breaks local demo mode silently while the suite stays green. This already
  happened once in Task 1. Use `grep -rn "<name>" --include="*.py" . | grep -v node_modules`.
- **`kill %1` does not stop uvicorn.** `uv run` spawns a child, so killing the job leaves the
  server bound to port 8000 and the next task's live check fails confusingly. After any live
  check run:
  ```bash
  kill %1 2>/dev/null; pkill -f "uvicorn backend.app.main:app" 2>/dev/null
  lsof -i :8000 || echo "port 8000 free"
  ```

## Critical Domain Facts

Read these before writing any code. They are the non-obvious things that will otherwise be got wrong.

### `meal_calorie_budget_kcal` is a DAILY figure, not a per-meal figure

`CalorieExpenditureAgent._meal_budget` (`backend/app/agents/calorie_expenditure_agent.py:147-155`) returns
`expenditure` adjusted only by goal: `-400` to cut, `+250` to bulk, unchanged to maintain.
`backend/tests/test_calorie_expenditure_agent.py:34` asserts it **equals** daily expenditure for `maintain`.
The name is wrong, and both UIs currently display it labelled as a meal budget.

**For this phase: pass it as the DAILY target.** `MealRecommendationAgent._scale_ingredients_to_meal_target`
already derives the true per-meal number as `clamp(350, 850, daily * 0.28)` and exposes it as
`portion_scaling.target_meal_calories`. Do **not** rename the field — that is an API-breaking
change touching both clients, and it is tracked separately in `docs/4_next_steps.md`.
Do **not** multiply the budget by 0.28 yourself; the meal agent does that.

### The profile dict → `CalorieExpenditureRequest` mapping

`UserProfileRepository.fetch_user_profile(user_id)` returns keys
`age, gender, weight, height, workout_level, dietary_restrictions`
(`backend/app/repositories/storage.py:26-38`). `CalorieExpenditureRequest` wants
`age, sex, height_cm, weight_kg, activity_multiplier`. The mapping is
`gender→sex`, `weight→weight_kg`, `height→height_cm`, `workout_level→activity_multiplier`.
`CalorieExpenditureRequest` validates `activity_multiplier` as `gt=1.0, le=2.5`; the default
profile's `workout_level` is `1.55`, which is valid.

### The three `AgentMetadata` classes are not identical

`meal_recommendation_agent.py:25` has an extra `explanation: str | None = None`;
`nutrition_verification_agent.py:28` and `supermarket_agent.py:27` do not.
Collapsing all three into one class with `explanation` would add `"explanation": null`
to the nutrition and shopping-list responses — a response-shape change. Use a base class
plus a subclass instead (Task 4).

---

## File Structure

**Created:**

| File | Responsibility |
| --- | --- |
| `backend/app/schemas/common.py` | The one `AgentMetadata`, `MealAgentMetadata`, and `average_confidence` |
| `backend/app/schemas/responses.py` | One response model per endpoint |
| `backend/app/core/exceptions.py` | Domain exceptions + the FastAPI handlers |
| `backend/app/core/container.py` | Builds agents/repositories once; `Depends()` providers |
| `backend/app/services/meal_planning_service.py` | The orchestrator |
| `backend/app/api/routes/{health,meal_plans,calories,feedback}.py` | Routers |
| `backend/app/rag/reference_data.py` | Loads `data/reference/*.json` once, cached |
| `data/reference/{ingredient_calories,macro_fallbacks,trusted_overrides,supermarket_prices,fallback_meals}.json` | Tables extracted from agent methods |
| `backend/tests/test_meal_planning_service.py` | Orchestrator + calorie wiring + reconciliation |
| `backend/tests/test_api_endpoints.py` | `TestClient` coverage of all 8 routes |
| `backend/tests/test_reference_data.py` | Extracted tables match the old hardcoded values |

**Modified:** `backend/app/main.py` (shrinks to app construction), all four agents, `backend/app/schemas/requests.py`.

---

## Task 1: Orchestrator service and calorie wiring

The headline fix (DEC-3): the trained model currently never reaches meal planning.

**Files:**
- Create: `backend/app/services/meal_planning_service.py`
- Create: `backend/tests/test_meal_planning_service.py`
- Modify: `backend/app/agents/meal_recommendation_agent.py` (delete `calculate_bmr`, accept a budget)
- Modify: `backend/app/schemas/requests.py` (optional biometrics on `MealRequest`)
- Modify: `backend/app/main.py` (call the service)

**Interfaces:**
- Produces: `MealPlanningService(meal_agent, nutrition_agent, supermarket_agent, calorie_agent, profile_repo)` with `generate(request: MealRequest) -> MealPlanResult`. `MealPlanResult` is a Pydantic model with fields `calorie_budget: CalorieExpenditureResponse`, `meal_plan: MealPlanPayload`, `nutrition: MealNutrition`, `shopping_list: SupermarketPayload`, `reconciliation: ReconciliationMetadata | None`. Task 2 adds the reconciliation field's population; Task 7 injects the service; Task 9 wraps the result in a response model.
- Consumes: nothing from later tasks.

- [ ] **Step 1: Add optional biometrics to `MealRequest`**

In `backend/app/schemas/requests.py`, add to `MealRequest` (keep existing fields unchanged):

```python
    age: int | None = Field(default=None, gt=0, le=120)
    sex: str | None = Field(default=None, min_length=1, max_length=16)
    height_cm: float | None = Field(default=None, gt=80, le=260)
    weight_kg: float | None = Field(default=None, gt=20, le=350)
    activity_multiplier: float | None = Field(default=None, gt=1.0, le=2.5)
    goal: str = Field(default="maintain", min_length=3, max_length=40)
```

Bounds are copied verbatim from `CalorieExpenditureRequest` so the two validate identically.

- [ ] **Step 2: Write the failing tests**

Create `backend/tests/test_meal_planning_service.py`:

```python
"""Tests for the meal planning orchestrator."""

from backend.app.agents.calorie_expenditure_agent import CalorieExpenditureAgent
from backend.app.agents.meal_recommendation_agent import MealRecommendationAgent
from backend.app.agents.nutrition_verification_agent import NutritionVerificationAgent
from backend.app.agents.supermarket_agent import SupermarketAgent
from backend.app.core.config import AppSettings
from backend.app.repositories.storage import UserProfileRepository
from backend.app.schemas.requests import MealRequest
from backend.app.services.meal_planning_service import MealPlanningService


def _service() -> MealPlanningService:
    settings = AppSettings.from_env()
    return MealPlanningService(
        meal_agent=MealRecommendationAgent(
            db_connection=UserProfileRepository(settings.data_dir),
            meal_corpus_path=settings.meal_corpus_path,
        ),
        nutrition_agent=NutritionVerificationAgent(),
        supermarket_agent=SupermarketAgent(),
        calorie_agent=CalorieExpenditureAgent(
            model_path=settings.calorie_model_path,
            model_version=settings.calorie_model_version,
        ),
        profile_repo=UserProfileRepository(settings.data_dir),
    )


def test_service_uses_calorie_agent_budget_as_the_meal_target() -> None:
    """The meal plan's caloric target must come from the calorie agent, not a local BMR."""
    result = _service().generate(
        MealRequest(user_id="user_123", craving="high-protein burger", location="Earlwood, NSW")
    )

    assert result.calorie_budget.meal_calorie_budget_kcal > 0
    # The meal agent receives the DAILY budget; user_context echoes exactly that.
    assert result.meal_plan.user_context.caloric_target == int(
        round(result.calorie_budget.meal_calorie_budget_kcal)
    )


def test_service_prefers_request_biometrics_over_the_stored_profile() -> None:
    """Explicit biometrics on the request override the stored profile."""
    light = _service().generate(
        MealRequest(craving="salad", age=25, sex="female", height_cm=160,
                    weight_kg=55, activity_multiplier=1.2)
    )
    heavy = _service().generate(
        MealRequest(craving="salad", age=25, sex="male", height_cm=195,
                    weight_kg=100, activity_multiplier=1.9)
    )
    assert heavy.calorie_budget.estimated_daily_expenditure_kcal > (
        light.calorie_budget.estimated_daily_expenditure_kcal
    )


def test_service_goal_shifts_the_budget() -> None:
    """A cutting goal must produce a lower budget than bulking, all else equal."""
    cut = _service().generate(MealRequest(craving="salad", goal="cut"))
    bulk = _service().generate(MealRequest(craving="salad", goal="bulk"))
    assert cut.calorie_budget.meal_calorie_budget_kcal < (
        bulk.calorie_budget.meal_calorie_budget_kcal
    )


def test_service_returns_every_section() -> None:
    """The orchestrator returns all four agent payloads."""
    result = _service().generate(MealRequest(craving="pasta"))
    assert result.meal_plan.meal_definition.ingredients
    assert result.nutrition.total_calories > 0
    assert result.shopping_list.shopping_list
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `uv run pytest backend/tests/test_meal_planning_service.py`
Expected: FAIL — `ModuleNotFoundError: No module named 'backend.app.services.meal_planning_service'`

- [ ] **Step 4: Change the meal agent to accept a budget instead of computing BMR**

In `backend/app/agents/meal_recommendation_agent.py`, **delete the whole `calculate_bmr` method**
(lines 120-134) and change `generate_meal_payload` to take the target as a parameter.

Replace the head of `generate_meal_payload`:

```python
    def generate_meal_payload(
        self,
        craving: str,
        user_id: str,
        daily_calorie_target: int,
        health_conditions: list[str] | None = None,
        dietary_preferences: list[str] | None = None,
    ) -> MealPlanPayload:
        """Retrieve and adapt a meal for the given craving and calorie target.

        Args:
            craving: Free-text craving from the user.
            user_id: Profile key used to look up dietary restrictions.
            daily_calorie_target: Daily kcal target from CalorieExpenditureAgent.
                This is a DAILY figure; portion scaling derives the per-meal
                target from it.
            health_conditions: Conditions that hard-filter the corpus.
            dietary_preferences: Soft preferences that bias ranking.

        Returns:
            A populated MealPlanPayload.
        """
        user_biometrics = self.db.fetch_user_profile(user_id)
        target_calories = daily_calorie_target
```

Everything from `health_conditions = health_conditions or []` onward stays exactly as it is.
`user_biometrics` is still needed for `dietary_restrictions` and `_fallback_payload`.

- [ ] **Step 5: Write the orchestrator**

Create `backend/app/services/meal_planning_service.py`:

```python
"""Orchestrates the multi-agent meal planning workflow."""

import logging
from typing import Any

from pydantic import BaseModel

from ..agents.calorie_expenditure_agent import (
    CalorieExpenditureAgent,
    CalorieExpenditureRequest,
    CalorieExpenditureResponse,
)
from ..agents.meal_recommendation_agent import MealPlanPayload, MealRecommendationAgent
from ..agents.nutrition_verification_agent import MealNutrition, NutritionVerificationAgent
from ..agents.supermarket_agent import SupermarketAgent, SupermarketPayload
from ..schemas.requests import MealRequest

logger = logging.getLogger(__name__)


class MealPlanResult(BaseModel):
    """Everything the meal-plan endpoint needs, assembled by the orchestrator."""

    calorie_budget: CalorieExpenditureResponse
    meal_plan: MealPlanPayload
    nutrition: MealNutrition
    shopping_list: SupermarketPayload


class MealPlanningService:
    """Coordinates the calorie, meal, nutrition and supermarket agents.

    The orchestrator owns the workflow so no agent needs to know about another.
    """

    def __init__(
        self,
        meal_agent: MealRecommendationAgent,
        nutrition_agent: NutritionVerificationAgent,
        supermarket_agent: SupermarketAgent,
        calorie_agent: CalorieExpenditureAgent,
        profile_repo: Any,
    ) -> None:
        """Store the collaborating agents.

        Args:
            meal_agent: Retrieves and adapts a meal template.
            nutrition_agent: Verifies ingredient macros.
            supermarket_agent: Maps ingredients to a shopping list.
            calorie_agent: Predicts expenditure and the calorie budget.
            profile_repo: Supplies stored biometrics when the request omits them.
        """
        self.meal_agent = meal_agent
        self.nutrition_agent = nutrition_agent
        self.supermarket_agent = supermarket_agent
        self.calorie_agent = calorie_agent
        self.profile_repo = profile_repo

    def generate(self, request: MealRequest) -> MealPlanResult:
        """Run the full meal planning workflow.

        Args:
            request: The validated meal-plan request.

        Returns:
            A MealPlanResult carrying every agent payload.
        """
        calorie_budget = self.calorie_agent.predict(self._calorie_request(request))

        meal_plan = self.meal_agent.generate_meal_payload(
            craving=request.craving.strip(),
            user_id=request.user_id.strip(),
            daily_calorie_target=int(round(calorie_budget.meal_calorie_budget_kcal)),
            health_conditions=request.health_conditions,
            dietary_preferences=request.dietary_preferences,
        )
        nutrition = self.nutrition_agent.calculate_meal_macros(
            ingredients=meal_plan.meal_definition.ingredients
        )
        shopping_list = self.supermarket_agent.generate_shopping_list(
            ingredients=meal_plan.meal_definition.ingredients,
            user_location=request.location.strip(),
        )
        return MealPlanResult(
            calorie_budget=calorie_budget,
            meal_plan=meal_plan,
            nutrition=nutrition,
            shopping_list=shopping_list,
        )

    def _calorie_request(self, request: MealRequest) -> CalorieExpenditureRequest:
        """Build a calorie request, preferring explicit biometrics over the profile.

        Args:
            request: The meal-plan request, whose biometric fields are optional.

        Returns:
            A CalorieExpenditureRequest populated from the request or the profile.
        """
        profile = self.profile_repo.fetch_user_profile(request.user_id.strip())
        return CalorieExpenditureRequest(
            age=request.age if request.age is not None else profile["age"],
            sex=request.sex if request.sex is not None else profile["gender"],
            height_cm=(
                request.height_cm if request.height_cm is not None else profile["height"]
            ),
            weight_kg=(
                request.weight_kg if request.weight_kg is not None else profile["weight"]
            ),
            activity_multiplier=(
                request.activity_multiplier
                if request.activity_multiplier is not None
                else profile["workout_level"]
            ),
            goal=request.goal,
            health_conditions=request.health_conditions,
        )
```

- [ ] **Step 6: Run the new tests**

Run: `uv run pytest backend/tests/test_meal_planning_service.py`
Expected: PASS, 4 passed.

- [ ] **Step 7: Wire the service into `main.py`**

In `backend/app/main.py`, add the import alongside the other agent imports **in both branches of the
existing try/except block** (Task 3 removes that block; until then it must stay consistent):

```python
    from .services.meal_planning_service import MealPlanningService
```
and in the `except ImportError` branch:
```python
    from backend.app.services.meal_planning_service import MealPlanningService
```

After `calorie_expenditure_agent = CalorieExpenditureAgent(...)`, add:

```python
meal_planning_service = MealPlanningService(
    meal_agent=meal_recommendation_agent,
    nutrition_agent=nutrition_verification_agent,
    supermarket_agent=supermarket_agent,
    calorie_agent=calorie_expenditure_agent,
    profile_repo=user_profiles,
)
```

Then replace the body of `generate_meal_plan`'s `try:` block — everything from
`active_meal_agent = meal_recommendation_agent` down to and including the `response = {...}`
assignment — with:

```python
        service = meal_planning_service
        if x_gemini_api_key and not settings.gemini_api_key:
            # Reuse the already-built retriever instead of re-embedding the corpus.
            service = MealPlanningService(
                meal_agent=MealRecommendationAgent(
                    db_connection=user_profiles,
                    gemini_api_key=x_gemini_api_key,
                    meal_retriever=meal_recommendation_agent.meal_retriever,
                    enable_llm_adaptation=settings.enable_gemini_adaptation,
                ),
                nutrition_agent=nutrition_verification_agent,
                supermarket_agent=supermarket_agent,
                calorie_agent=calorie_expenditure_agent,
                profile_repo=user_profiles,
            )

        result = await run_in_threadpool(service.generate, request)

        response = {
            "status": "success",
            "request_id": request_id,
            "generated_at": generated_at,
            "request": request.model_dump(),
            "calorie_budget": result.calorie_budget.model_dump(),
            "meal_plan": result.meal_plan.model_dump(),
            "nutrition": result.nutrition.model_dump(),
            "shopping_list": result.shopping_list.model_dump(),
        }
```

The `await run_in_threadpool(meal_history.save, response)` and `return response` lines stay.

- [ ] **Step 8: Run the whole suite**

Run: `uv run pytest`
Expected: **23 passed** (19 baseline + 4 new). If any pre-existing test fails, the meal agent's
signature change broke a caller — fix the caller, never the test's assertions.

- [ ] **Step 9: Confirm the wiring end to end against a running server**

```bash
cp backend/.env.example backend/.env
uv run uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 &
sleep 8
curl -s -X POST http://127.0.0.1:8000/generate-meal-plan \
  -H 'Content-Type: application/json' \
  -d '{"user_id":"user_123","craving":"high-protein burger","location":"Earlwood, NSW"}' \
  | uv run python -c "import json,sys; d=json.load(sys.stdin); print('model_version:', d['calorie_budget']['model_version']); print('budget:', d['calorie_budget']['meal_calorie_budget_kcal']); print('target:', d['meal_plan']['user_context']['caloric_target']); print('per-meal:', d['meal_plan']['portion_scaling']['target_meal_calories'])"
kill %1
```

Expected: `model_version` is `hist_gradient_boosting_deep_v0.1.0` (**not** `mifflin_st_jeor_fallback_v0.1.0` — that would mean the artifact failed to load), `budget` equals `target`, and `per-meal` is between 350 and 850. Kill the server; confirm nothing is left on port 8000.

- [ ] **Step 10: Lint, then commit**

```bash
uv run ruff check . && uv run ruff format --check .
git status --short
git add backend/app/services/meal_planning_service.py backend/tests/test_meal_planning_service.py backend/app/agents/meal_recommendation_agent.py backend/app/schemas/requests.py backend/app/main.py
git commit -F - <<'MSG'
feat(services): wire the trained calorie model into meal planning

The repository shipped a trained calorie model that /generate-meal-plan never
called: MealRecommendationAgent computed its own Mifflin-St Jeor BMR while
CalorieExpenditureAgent - and its meal_calorie_budget_kcal - were reachable only
through /calorie-expenditure/predict. Spec section 6 item 1, DEC-3.

Adds services/meal_planning_service.py as the orchestrator. It predicts the
budget, passes it to the meal agent, verifies nutrition and builds the shopping
list, so no agent has to know about another. MealRequest gains optional
biometrics, which override the stored profile when present; the profile supplies
them otherwise. calculate_bmr is deleted from the meal agent, which now takes
daily_calorie_target as a parameter.

Note meal_calorie_budget_kcal is a DAILY figure despite its name - the meal
agent derives the per-meal target from it as clamp(350, 850, daily * 0.28) and
reports it as portion_scaling.target_meal_calories. The rename is API-breaking
for both clients and is tracked in docs/4_next_steps.md rather than done here.

The response gains a calorie_budget section.

Verified: 23 tests pass (19 baseline + 4 new). A live POST returns
model_version hist_gradient_boosting_deep_v0.1.0, with the meal plan's
caloric_target equal to the agent's budget.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
MSG
```

---

## Task 2: Reconciliation loop

Spec §6 item 2, and steps 5-6 of the documented workflow, which have never been implemented.

**Files:**
- Modify: `backend/app/services/meal_planning_service.py`
- Modify: `backend/tests/test_meal_planning_service.py`

**Interfaces:**
- Consumes: `MealPlanningService.generate` and `MealPlanResult` from Task 1.
- Produces: `ReconciliationMetadata` on `MealPlanResult.reconciliation`, with fields
  `target_meal_calories: int`, `verified_calories_before: float`, `deviation_before: float`,
  `rescaled: bool`, `verified_calories_after: float | None`, `deviation_after: float | None`,
  `within_tolerance: bool`, `tolerance: float`. Task 9 exposes it in the response model.

- [ ] **Step 1: Write the failing tests**

Append to `backend/tests/test_meal_planning_service.py`:

```python
def test_reconciliation_metadata_is_always_reported() -> None:
    """Every plan reports how the estimate compared with verified nutrition."""
    result = _service().generate(MealRequest(craving="high-protein burger"))
    rec = result.reconciliation
    assert rec is not None
    assert rec.tolerance == 0.15
    assert rec.target_meal_calories > 0
    assert rec.verified_calories_before > 0
    assert rec.deviation_before >= 0


def test_reconciliation_retries_at_most_once() -> None:
    """A rescale happens at most one time, never in a loop."""
    result = _service().generate(MealRequest(craving="pasta"))
    rec = result.reconciliation
    assert rec is not None
    if rec.rescaled:
        assert rec.verified_calories_after is not None
        assert rec.deviation_after is not None
        # One retry only: after-values exist, and no third figure is reported.
        assert rec.deviation_after <= rec.deviation_before
    else:
        assert rec.verified_calories_after is None
        assert rec.within_tolerance is True


def test_reconciliation_rescale_moves_nutrition_toward_the_target() -> None:
    """When a rescale happens, the returned nutrition reflects the rescaled portions."""
    result = _service().generate(MealRequest(craving="high-protein burger"))
    rec = result.reconciliation
    assert rec is not None
    if rec.rescaled:
        assert result.nutrition.total_calories == rec.verified_calories_after
```

- [ ] **Step 2: Run to verify failure**

Run: `uv run pytest backend/tests/test_meal_planning_service.py`
Expected: FAIL — `AttributeError: 'MealPlanResult' object has no attribute 'reconciliation'`

- [ ] **Step 3: Add the model and the reconciliation step**

In `backend/app/services/meal_planning_service.py`, add the import for `Ingredient`:

```python
from ..schemas.requests import Ingredient, MealRequest
```

Add above `MealPlanResult`:

```python
DEFAULT_TOLERANCE = 0.15
"""Fractional deviation between the portion estimate and verified nutrition that
is accepted without rescaling."""


class ReconciliationMetadata(BaseModel):
    """Records how the portion estimate compared with verified nutrition."""

    target_meal_calories: int
    verified_calories_before: float
    deviation_before: float
    rescaled: bool
    verified_calories_after: float | None = None
    deviation_after: float | None = None
    within_tolerance: bool
    tolerance: float
```

Add `reconciliation: ReconciliationMetadata | None = None` to `MealPlanResult`.

Add `tolerance: float = DEFAULT_TOLERANCE` as the last `__init__` parameter, stored as
`self.tolerance = tolerance`, and document it in the docstring as
"Accepted fractional deviation before portions are rescaled."

In `generate`, replace the block from `nutrition = ...` to the `return` with:

```python
        nutrition = self.nutrition_agent.calculate_meal_macros(
            ingredients=meal_plan.meal_definition.ingredients
        )
        meal_plan, nutrition, reconciliation = self._reconcile(meal_plan, nutrition)

        shopping_list = self.supermarket_agent.generate_shopping_list(
            ingredients=meal_plan.meal_definition.ingredients,
            user_location=request.location.strip(),
        )
        return MealPlanResult(
            calorie_budget=calorie_budget,
            meal_plan=meal_plan,
            nutrition=nutrition,
            shopping_list=shopping_list,
            reconciliation=reconciliation,
        )
```

Note the shopping list is built **after** reconciliation, so it prices the portions actually served.

Add the method:

```python
    def _reconcile(
        self,
        meal_plan: MealPlanPayload,
        nutrition: MealNutrition,
    ) -> tuple[MealPlanPayload, MealNutrition, ReconciliationMetadata | None]:
        """Compare verified nutrition against the portion target, rescaling once if needed.

        Args:
            meal_plan: The plan whose portions were scaled from an estimate.
            nutrition: Verified macros for those portions.

        Returns:
            The plan, the nutrition and the reconciliation record. When portion
            scaling did not run there is nothing to reconcile against, so the
            record is None and the inputs are returned unchanged.
        """
        scaling = meal_plan.portion_scaling
        if scaling is None or nutrition.total_calories <= 0:
            return meal_plan, nutrition, None

        target = scaling.target_meal_calories
        before = nutrition.total_calories
        deviation_before = abs(before - target) / target

        if deviation_before <= self.tolerance:
            return meal_plan, nutrition, ReconciliationMetadata(
                target_meal_calories=target,
                verified_calories_before=round(before, 1),
                deviation_before=round(deviation_before, 4),
                rescaled=False,
                within_tolerance=True,
                tolerance=self.tolerance,
            )

        factor = max(0.65, min(1.6, target / before))
        rescaled_ingredients = [
            Ingredient(
                item_name=ingredient.item_name,
                base_quantity_grams=max(
                    5, int(round(ingredient.base_quantity_grams * factor / 5) * 5)
                ),
            )
            for ingredient in meal_plan.meal_definition.ingredients
        ]
        meal_plan.meal_definition.ingredients = rescaled_ingredients

        # Exactly one retry. Whatever this produces is what ships.
        nutrition = self.nutrition_agent.calculate_meal_macros(ingredients=rescaled_ingredients)
        after = nutrition.total_calories
        deviation_after = abs(after - target) / target if after > 0 else deviation_before

        meal_plan.metadata.warnings.append(
            f"Rescaled portions by {factor:.2f} after verified nutrition deviated "
            f"{deviation_before:.0%} from the {target} kcal target."
        )
        return meal_plan, nutrition, ReconciliationMetadata(
            target_meal_calories=target,
            verified_calories_before=round(before, 1),
            deviation_before=round(deviation_before, 4),
            rescaled=True,
            verified_calories_after=round(after, 1),
            deviation_after=round(deviation_after, 4),
            within_tolerance=deviation_after <= self.tolerance,
            tolerance=self.tolerance,
        )
```

The `0.65`/`1.6` clamp matches `_scale_ingredients_to_meal_target` in the meal agent, so a
rescale can never push portions outside the range the first scaling already allowed.

- [ ] **Step 4: Run the tests**

Run: `uv run pytest backend/tests/test_meal_planning_service.py`
Expected: PASS, 7 passed.

- [ ] **Step 5: Add the reconciliation section to the response**

In `backend/app/main.py`, inside `generate_meal_plan`'s `response = {...}`, add after
`"shopping_list": ...`:

```python
            "reconciliation": (
                result.reconciliation.model_dump() if result.reconciliation else None
            ),
```

- [ ] **Step 6: Full suite and a live check**

```bash
uv run pytest
```
Expected: **26 passed**.

```bash
uv run uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 &
sleep 8
curl -s -X POST http://127.0.0.1:8000/generate-meal-plan -H 'Content-Type: application/json' \
  -d '{"craving":"high-protein burger"}' \
  | uv run python -c "import json,sys; print(json.load(sys.stdin)['reconciliation'])"
kill %1
```
Expected: a dict with `tolerance: 0.15` and a boolean `within_tolerance`. Kill the server.

- [ ] **Step 7: Lint and commit**

```bash
uv run ruff check . && uv run ruff format --check .
git status --short
git add backend/app/services/meal_planning_service.py backend/tests/test_meal_planning_service.py backend/app/main.py
git commit -F - <<'MSG'
feat(services): reconcile verified nutrition against the portion target

Steps 5 and 6 of the documented workflow - compare the generated estimate with
the verified total, and revise portions when it falls outside tolerance - had
never been implemented. Spec section 6 item 2.

The orchestrator now compares verified nutrition against
portion_scaling.target_meal_calories. Within 15% it records the comparison and
moves on. Outside it, portions are rescaled once by target/verified, clamped to
the same 0.65-1.6 range the meal agent's own scaling uses, then re-verified.
Exactly one retry, never a loop.

The shopping list is now built after reconciliation so it prices the portions
actually served, not the pre-rescale ones.

Every response carries a reconciliation section, so a reader can see the
deviation even when nothing was rescaled.

Verified: 26 tests pass. A live POST returns reconciliation with tolerance 0.15
and a within_tolerance verdict.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
MSG
```

---

## Task 3: Delete the dual-import block and the dead code

**Files:**
- Modify: `backend/app/main.py:11-40`
- Modify: `backend/app/agents/meal_recommendation_agent.py` (remove two dead methods)

**Interfaces:**
- Consumes: the hatchling packaging landed in Phase 0, which makes `from backend.app...` always resolve.
- Produces: a `main.py` with a single import block.

- [ ] **Step 1: Prove the fallback import branch is unnecessary**

```bash
uv run python -c "from backend.app.services.meal_planning_service import MealPlanningService; print('ok')"
cd /tmp && uv run --project "/Users/tuannm3812/Documents/GitHub/1. Study/ai-meal-planner" python -c "from backend.app.core.config import AppSettings; print('resolves from any cwd')"
```
Expected: both print. Phase 0 installed the project, so the relative-import fallback is dead weight.

- [ ] **Step 2: Collapse the import block**

In `backend/app/main.py`, replace the entire `try: ... except ImportError: ...` block (lines 11-40)
with the absolute imports only:

```python
from backend.app.agents.calorie_expenditure_agent import (
    CalorieExpenditureAgent,
    CalorieExpenditureRequest,
)
from backend.app.agents.meal_recommendation_agent import MealRecommendationAgent
from backend.app.agents.nutrition_verification_agent import NutritionVerificationAgent
from backend.app.agents.supermarket_agent import SupermarketAgent
from backend.app.core.config import AppSettings
from backend.app.repositories.storage import (
    MealFeedbackRepository,
    MealPlanRepository,
    UserProfileRepository,
)
from backend.app.schemas.requests import MealFeedbackRequest, MealRequest
from backend.app.services.meal_planning_service import MealPlanningService
```

- [ ] **Step 3: Delete the dead preference-modelling code**

In `backend/app/agents/meal_recommendation_agent.py` delete both methods entirely:
`predict_user_preferences` (line 179) and `_initialize_preference_classifier` (line 513).
The second only ever raised `NotImplementedError`; the first called it, and nothing calls either.

Confirm nothing referenced them:
```bash
grep -rn "predict_user_preferences\|_initialize_preference_classifier" --include="*.py" .
```
Expected: no output.

- [ ] **Step 4: Verify**

```bash
uv run pytest
uv run ruff check . && uv run ruff format --check .
uv run uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 &
sleep 8
curl -s http://127.0.0.1:8000/health | head -c 120
kill %1
```
Expected: **26 passed**, ruff clean, `/health` returns `"status":"ok"`.

- [ ] **Step 5: Commit**

```bash
git status --short
git add backend/app/main.py backend/app/agents/meal_recommendation_agent.py
git commit -F - <<'MSG'
refactor(api): drop the dual-import fallback and dead preference code

main.py imported every symbol twice, once relatively and once absolutely, inside
a try/except ImportError that worked around package-path ambiguity. Phase 0
packaged backend with hatchling, so from backend.app... now resolves from any
working directory and the fallback branch is unreachable. Verified by importing
from /tmp before deleting it.

Also removes MealRecommendationAgent.predict_user_preferences and
_initialize_preference_classifier. The latter only ever raised
NotImplementedError, the former called it, and nothing called either. Preference
learning is tracked in docs/4_next_steps.md.

Verified: 26 tests pass, ruff clean, /health returns ok.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
MSG
```

---

## Task 4: Deduplicate `AgentMetadata` and the confidence helper

**Files:**
- Create: `backend/app/schemas/common.py`
- Modify: all three agents that define `AgentMetadata`

**Interfaces:**
- Produces: `backend.app.schemas.common.AgentMetadata` (fields `agent_name: str`, `source: str`,
  `confidence: float`, `warnings: list[str]`), `MealAgentMetadata(AgentMetadata)` adding
  `explanation: str | None = None`, and `average_confidence(items: Sequence[Any]) -> float`.

**Read the Critical Domain Facts note first:** the meal agent's `AgentMetadata` has an extra
`explanation` field. Collapsing all three into one class would add `"explanation": null` to the
nutrition and shopping-list responses. Use the base/subclass split below.

- [ ] **Step 1: Write the failing test**

Create `backend/tests/test_schemas_common.py`:

```python
"""Tests for the shared schema helpers."""

import pytest
from pydantic import BaseModel, Field

from backend.app.schemas.common import AgentMetadata, MealAgentMetadata, average_confidence


class _Scored(BaseModel):
    confidence: float = Field(ge=0, le=1)


def test_agent_metadata_has_no_explanation_field() -> None:
    """The base metadata must not add an explanation key to agent responses."""
    assert "explanation" not in AgentMetadata.model_fields


def test_meal_agent_metadata_adds_explanation() -> None:
    """Only the meal agent carries an explanation."""
    assert "explanation" in MealAgentMetadata.model_fields
    assert MealAgentMetadata(agent_name="a", source="s", confidence=0.5).explanation is None


def test_average_confidence_rounds_to_two_places() -> None:
    # round(0.625, 2) is 0.62, not 0.63 - Python rounds halves to even. Both original
    # _average_confidence implementations produced 0.62, so this preserves behaviour.
    assert average_confidence([_Scored(confidence=0.5), _Scored(confidence=0.75)]) == 0.62


def test_average_confidence_of_nothing_is_zero() -> None:
    """An empty list must not raise ZeroDivisionError."""
    assert average_confidence([]) == 0.0


@pytest.mark.parametrize("bad", [-0.1, 1.1])
def test_agent_metadata_rejects_out_of_range_confidence(bad: float) -> None:
    with pytest.raises(ValueError):
        AgentMetadata(agent_name="a", source="s", confidence=bad)
```

- [ ] **Step 2: Run to verify failure**

Run: `uv run pytest backend/tests/test_schemas_common.py`
Expected: FAIL — `ModuleNotFoundError: No module named 'backend.app.schemas.common'`

- [ ] **Step 3: Check what the existing helpers actually do before replacing them**

```bash
sed -n '/def _average_confidence/,/^$/p' backend/app/agents/nutrition_verification_agent.py
sed -n '/def _average_confidence/,/^$/p' backend/app/agents/supermarket_agent.py
```
Both must round to 2 places and return `0.0` for an empty list. If either differs, match the
existing behaviour and say so in your report rather than changing behaviour here.

- [ ] **Step 4: Write the module**

Create `backend/app/schemas/common.py`:

```python
"""Schema fragments shared by more than one agent."""

from collections.abc import Sequence
from typing import Any

from pydantic import BaseModel, Field


class AgentMetadata(BaseModel):
    """Provenance and confidence reported by every agent."""

    agent_name: str
    source: str
    confidence: float = Field(ge=0, le=1)
    warnings: list[str] = Field(default_factory=list)


class MealAgentMetadata(AgentMetadata):
    """Meal-agent metadata, which may carry an LLM-generated explanation."""

    explanation: str | None = None


def average_confidence(items: Sequence[Any]) -> float:
    """Average the confidence of scored items.

    Args:
        items: Objects exposing a numeric ``confidence`` attribute.

    Returns:
        The mean confidence rounded to two places, or 0.0 when there is nothing
        to average.
    """
    if not items:
        return 0.0
    return round(sum(item.confidence for item in items) / len(items), 2)
```

- [ ] **Step 5: Run the new test**

Run: `uv run pytest backend/tests/test_schemas_common.py`
Expected: PASS, 6 passed.

- [ ] **Step 6: Replace the three duplicates**

In `backend/app/agents/nutrition_verification_agent.py`: delete its local `class AgentMetadata`,
import `from ..schemas.common import AgentMetadata, average_confidence`, delete its
`_average_confidence` static method, and change the call site
`confidence = self._average_confidence(processed_ingredients)` to
`confidence = average_confidence(processed_ingredients)`.

In `backend/app/agents/supermarket_agent.py`: identically — delete the local class and static
method, import the shared ones, and change `self._average_confidence(shopping_list_items)` to
`average_confidence(shopping_list_items)`.

In `backend/app/agents/meal_recommendation_agent.py`: delete its local `class AgentMetadata` and
import `from ..schemas.common import MealAgentMetadata as AgentMetadata`. Aliasing on import
keeps every existing `AgentMetadata(...)` construction site unchanged while preserving the
`explanation` field the meal agent sets in `_adapt_final_payload`.

- [ ] **Step 7: Prove the response shapes did not change**

```bash
uv run python -c "
from backend.app.agents.nutrition_verification_agent import MealNutrition
from backend.app.agents.supermarket_agent import SupermarketPayload
from backend.app.agents.meal_recommendation_agent import MealPlanPayload
import json
n = MealNutrition.model_json_schema()['\$defs']['AgentMetadata']['properties']
m = MealPlanPayload.model_json_schema()['\$defs']['MealAgentMetadata']['properties']
print('nutrition metadata keys:', sorted(n))
print('meal metadata keys:', sorted(m))
assert 'explanation' not in n, 'nutrition response gained an explanation key'
assert 'explanation' in m
print('OK - shapes preserved')
"
```
Expected: `OK - shapes preserved`.

- [ ] **Step 8: Verify and commit**

```bash
uv run pytest
```
Expected: **32 passed** (26 + 6 new). If any pre-existing test fails, a construction site
still passes a field the shared class does not accept — fix the call, not the schema.

```bash
uv run ruff check . && uv run ruff format --check .
git status --short
git add backend/app/schemas/common.py backend/tests/test_schemas_common.py backend/app/agents/nutrition_verification_agent.py backend/app/agents/supermarket_agent.py backend/app/agents/meal_recommendation_agent.py
git commit -F - <<'MSG'
refactor(schemas): collapse the duplicated AgentMetadata and confidence helper

AgentMetadata was defined three times, once per agent, and _average_confidence
twice. Spec section 6 item 7.

The three definitions were not identical: the meal agent's carries an extra
explanation field. Collapsing all three into one class would have added
"explanation": null to the nutrition and shopping-list responses, so
schemas/common.py provides AgentMetadata plus a MealAgentMetadata subclass. The
meal agent imports the subclass under the old name, leaving its construction
sites untouched.

Verified: 32 tests pass, ruff clean, and a JSON-schema check confirms the
nutrition response still has no explanation key while the meal response does.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
MSG
```

---

## Task 5: Extract the hardcoded reference tables to data files

Spec §6 item 9. The largest readability win: the agents keep the logic and lose the tables.

**Files:**
- Create: `data/reference/ingredient_calories.json`, `macro_fallbacks.json`, `trusted_overrides.json`, `supermarket_prices.json`, `fallback_meals.json`
- Create: `backend/app/rag/reference_data.py`
- Create: `backend/tests/test_reference_data.py`
- Modify: `backend/app/agents/meal_recommendation_agent.py`, `nutrition_verification_agent.py`, `supermarket_agent.py`

**Interfaces:**
- Produces: `backend.app.rag.reference_data.load_reference(name: str) -> dict[str, Any]`,
  cached with `functools.lru_cache`, resolving `<repo root>/data/reference/<name>.json`.

**This task must not change a single output value.** The test in Step 1 is what proves that.

- [ ] **Step 1: Capture the current values BEFORE changing anything**

```bash
uv run python - <<'PY'
import json
from backend.app.agents.meal_recommendation_agent import MealRecommendationAgent
from backend.app.agents.nutrition_verification_agent import NutritionVerificationAgent
from backend.app.agents.supermarket_agent import SupermarketAgent
from backend.app.schemas.requests import Ingredient

names = ["chicken breast", "brown rice", "olive oil", "firm tofu", "avocado",
         "salmon fillet", "rolled oats", "whole egg", "unknown mystery item"]
snap = {
  "calories": {n: MealRecommendationAgent._estimate_ingredient_calories(
        [Ingredient(item_name=n, base_quantity_grams=100)]) for n in names},
  "macros": {n: NutritionVerificationAgent()._estimate_macros_per_100g(n) for n in names},
  "overrides": {n: NutritionVerificationAgent._trusted_local_override(n) for n in names},
  "prices": {n: SupermarketAgent()._map_inventory_and_price(n) for n in names},
}
open("/tmp/reference_snapshot.json", "w").write(json.dumps(snap, indent=2, sort_keys=True))
print("captured", len(names), "ingredients")
PY
```
Keep `/tmp/reference_snapshot.json`. Step 6 diffs against it.

- [ ] **Step 2: Write the loader**

Create `backend/app/rag/reference_data.py`:

```python
"""Loads the JSON reference tables the agents use for local estimates."""

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

REFERENCE_DIR = Path(__file__).resolve().parents[3] / "data" / "reference"


@lru_cache(maxsize=None)
def load_reference(name: str) -> dict[str, Any]:
    """Load and cache one reference table.

    Args:
        name: File stem under ``data/reference``, e.g. ``ingredient_calories``.

    Returns:
        The parsed JSON object.

    Raises:
        FileNotFoundError: If the table is missing, which is a packaging error
            rather than a runtime condition worth degrading over.
    """
    path = REFERENCE_DIR / f"{name}.json"
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)
```

`parents[3]` resolves `backend/app/rag/reference_data.py` → repo root. Verify:
```bash
uv run python -c "from backend.app.rag.reference_data import REFERENCE_DIR; print(REFERENCE_DIR)"
```
Expected: `<repo>/data/reference`.

- [ ] **Step 3: Move each table, one at a time, verifying after each**

Do these **one at a time**, running `uv run pytest` after each. Moving all five before testing
makes a mismatch impossible to localise.

1. **`ingredient_calories.json`** — the `calories_per_100g` dict inside
   `MealRecommendationAgent._estimate_ingredient_calories`. Write it as a JSON object of
   `"name": number`. Replace the dict literal with
   `calories_per_100g = load_reference("ingredient_calories")`. **Keep the `120` default**
   for unknown ingredients exactly as it is.
2. **`macro_fallbacks.json`** — the table in `NutritionVerificationAgent._estimate_macros_per_100g`.
3. **`trusted_overrides.json`** — the table in `NutritionVerificationAgent._trusted_local_override`.
4. **`supermarket_prices.json`** — the table in `SupermarketAgent._map_inventory_and_price`.
5. **`fallback_meals.json`** — the craving `if/elif` chain in
   `MealRecommendationAgent._fallback_payload`. Shape it as a list so order is explicit and
   the first match wins, exactly as the chain did:
   ```json
   [
     {"keywords": ["noodle", "asian"], "meal_name": "High-Protein Asian Tofu Noodle Bowl",
      "ingredients": [{"item_name": "firm tofu", "base_quantity_grams": 180}]}
   ]
   ```
   The final `else` branch becomes the last entry with `"keywords": []`, matched only if
   nothing earlier did. Replace the chain with a loop over the loaded list; preserve the
   existing order — noodle/asian, pasta, salad, tofu/vegan, then the default.

- [ ] **Step 4: Write the regression test**

Create `backend/tests/test_reference_data.py`:

```python
"""Guards that extracting the reference tables changed no values."""

import pytest

from backend.app.agents.meal_recommendation_agent import MealRecommendationAgent
from backend.app.agents.nutrition_verification_agent import NutritionVerificationAgent
from backend.app.agents.supermarket_agent import SupermarketAgent
from backend.app.rag.reference_data import load_reference
from backend.app.schemas.requests import Ingredient


@pytest.mark.parametrize(
    ("item_name", "expected_kcal"),
    [("chicken breast", 165.0), ("olive oil", 884.0), ("brown rice", 123.0)],
)
def test_known_ingredient_calories_are_unchanged(item_name: str, expected_kcal: float) -> None:
    got = MealRecommendationAgent._estimate_ingredient_calories(
        [Ingredient(item_name=item_name, base_quantity_grams=100)]
    )
    assert got == pytest.approx(expected_kcal)


def test_unknown_ingredient_still_falls_back_to_120() -> None:
    """The default for an unlisted ingredient must not change."""
    got = MealRecommendationAgent._estimate_ingredient_calories(
        [Ingredient(item_name="nonexistent food", base_quantity_grams=100)]
    )
    assert got == pytest.approx(120.0)


def test_every_reference_table_loads() -> None:
    for name in (
        "ingredient_calories",
        "macro_fallbacks",
        "trusted_overrides",
        "supermarket_prices",
        "fallback_meals",
    ):
        assert load_reference(name)


def test_fallback_meals_end_with_an_unconditional_default() -> None:
    """The last entry matches anything, replacing the old else branch."""
    assert load_reference("fallback_meals")[-1]["keywords"] == []


def test_supermarket_prices_cover_the_priced_ingredients() -> None:
    agent = SupermarketAgent()
    priced = agent._map_inventory_and_price("chicken breast")
    assert priced["estimated_price"] > 0


def test_macro_fallbacks_still_produce_usable_macros() -> None:
    macros = NutritionVerificationAgent()._estimate_macros_per_100g("chicken breast")
    assert macros["calories_kcal"] > 0
```

- [ ] **Step 5: Run the tests**

Run: `uv run pytest`
Expected: **38 passed**.

- [ ] **Step 6: Diff against the pre-change snapshot — the real proof**

```bash
uv run python - <<'PY'
import json
from backend.app.agents.meal_recommendation_agent import MealRecommendationAgent
from backend.app.agents.nutrition_verification_agent import NutritionVerificationAgent
from backend.app.agents.supermarket_agent import SupermarketAgent
from backend.app.schemas.requests import Ingredient

names = ["chicken breast", "brown rice", "olive oil", "firm tofu", "avocado",
         "salmon fillet", "rolled oats", "whole egg", "unknown mystery item"]
now = {
  "calories": {n: MealRecommendationAgent._estimate_ingredient_calories(
        [Ingredient(item_name=n, base_quantity_grams=100)]) for n in names},
  "macros": {n: NutritionVerificationAgent()._estimate_macros_per_100g(n) for n in names},
  "overrides": {n: NutritionVerificationAgent._trusted_local_override(n) for n in names},
  "prices": {n: SupermarketAgent()._map_inventory_and_price(n) for n in names},
}
before = json.load(open("/tmp/reference_snapshot.json"))
if before == now:
    print("IDENTICAL - extraction changed no values")
else:
    for section in before:
        for k in before[section]:
            if before[section][k] != now[section].get(k):
                print("DIFF", section, k, before[section][k], "->", now[section].get(k))
    raise SystemExit("extraction changed values")
PY
```
Expected: `IDENTICAL - extraction changed no values`. **If it prints any DIFF, stop and fix the
data file** — do not proceed, and do not adjust the snapshot.

- [ ] **Step 7: Confirm the retrieval regression tests still pass**

```bash
uv run pytest backend/tests/test_retrieval_quality_regression.py backend/tests/test_meal_vector_rag.py
```
Expected: all pass. These guard the RAG behaviour that portion scaling feeds from.

- [ ] **Step 8: Commit**

```bash
uv run ruff check . && uv run ruff format --check .
git status --short
git add data/reference backend/app/rag/reference_data.py backend/tests/test_reference_data.py backend/app/agents/meal_recommendation_agent.py backend/app/agents/nutrition_verification_agent.py backend/app/agents/supermarket_agent.py
git commit -F - <<'MSG'
refactor(agents): move the reference tables out of agent methods into data files

Five lookup tables lived as literals inside agent methods: a 45-entry calorie
dict, the macro fallbacks, the trusted local overrides, roughly 100 lines of
supermarket price mapping, and the craving if/elif chain of fallback meal
templates. That is data, not code. Spec section 6 item 9.

They now live in data/reference/*.json, loaded once through
rag/reference_data.py with lru_cache. The agents keep their logic and lose the
tables. The fallback meals become an ordered list whose last entry has no
keywords, preserving the old chain's first-match-wins order and its else branch.

No output value changed. Proved by snapshotting every table's output for nine
ingredients before the extraction and diffing after: identical. The unknown
ingredient default of 120 kcal is preserved and now has its own test.

Verified: 38 tests pass, including the retrieval regression suite, ruff clean.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
MSG
```

---

## Task 6: Typed domain exceptions

Spec §6 item 8. Today every failure becomes a 500 whose body contains the raw exception string.

**Files:**
- Create: `backend/app/core/exceptions.py`
- Modify: `backend/app/main.py` (register handlers; stop catching bare `Exception`)

**Interfaces:**
- Produces: `MealPlanningError` (base), `ProfileNotFound`, `RetrievalUnavailable`,
  `NutritionProviderError`, each with a `status_code` class attribute and a `client_message`
  property; plus `register_exception_handlers(app: FastAPI) -> None`.

- [ ] **Step 1: Write the failing test**

Create `backend/tests/test_exceptions.py`:

```python
"""Domain exceptions must map to sane statuses and leak nothing internal."""

import pytest

from backend.app.core.exceptions import (
    MealPlanningError,
    NutritionProviderError,
    ProfileNotFound,
    RetrievalUnavailable,
)


@pytest.mark.parametrize(
    ("exc", "status"),
    [
        (ProfileNotFound("nope"), 404),
        (RetrievalUnavailable("index down"), 503),
        (NutritionProviderError("usda timeout"), 502),
        (MealPlanningError("generic"), 500),
    ],
)
def test_status_codes(exc: MealPlanningError, status: int) -> None:
    assert exc.status_code == status


def test_client_message_never_contains_internal_detail() -> None:
    """The message sent to a client must not echo the internal string."""
    exc = NutritionProviderError("postgres://user:password@host/db timed out")
    assert "password" not in exc.client_message
    assert "postgres" not in exc.client_message
    # The internal detail is still available for logs.
    assert "password" in str(exc)
```

- [ ] **Step 2: Run to verify failure**

Run: `uv run pytest backend/tests/test_exceptions.py`
Expected: FAIL — `ModuleNotFoundError: No module named 'backend.app.core.exceptions'`

- [ ] **Step 3: Write the module**

Create `backend/app/core/exceptions.py`:

```python
"""Domain exceptions and the handlers that map them to HTTP responses."""

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class MealPlanningError(Exception):
    """Base class for failures the API can describe to a client."""

    status_code = 500
    client_message = "Meal plan generation failed. Please try again."


class ProfileNotFound(MealPlanningError):
    """Raised when a requested user profile does not exist."""

    status_code = 404
    client_message = "No profile found for that user."


class RetrievalUnavailable(MealPlanningError):
    """Raised when the meal retrieval index cannot serve a query."""

    status_code = 503
    client_message = "Meal retrieval is temporarily unavailable. Please try again shortly."


class NutritionProviderError(MealPlanningError):
    """Raised when every nutrition provider fails for an ingredient."""

    status_code = 502
    client_message = "Nutrition verification is temporarily unavailable."


def register_exception_handlers(app: FastAPI) -> None:
    """Attach the domain exception handlers to an app.

    Args:
        app: The FastAPI application to register handlers on.
    """

    @app.exception_handler(MealPlanningError)
    async def _handle_domain_error(request: Request, exc: MealPlanningError) -> JSONResponse:
        # The internal string goes to logs; the client gets the safe message only.
        logger.warning("%s on %s: %s", type(exc).__name__, request.url.path, exc)
        return JSONResponse(
            status_code=exc.status_code,
            content={"status": "error", "error": type(exc).__name__,
                     "detail": exc.client_message},
        )

    @app.exception_handler(Exception)
    async def _handle_unexpected(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled error on %s", request.url.path)
        return JSONResponse(
            status_code=500,
            content={"status": "error", "error": "InternalServerError",
                     "detail": "An unexpected error occurred."},
        )
```

- [ ] **Step 4: Run the test**

Run: `uv run pytest backend/tests/test_exceptions.py`
Expected: PASS, 5 passed.

- [ ] **Step 5: Register the handlers and stop leaking exception strings**

In `backend/app/main.py`, import `register_exception_handlers` and call it right after
`app.add_middleware(...)`:

```python
register_exception_handlers(app)
```

Then in `generate_meal_plan`, **delete** the `try:`/`except Exception` wrapper entirely and
de-indent its body. The registered handlers now cover it, so a failure produces a logged
traceback and a safe client message instead of `detail=f"...: {exc}"`.

Keep the existing explicit `raise HTTPException(status_code=400, ...)` in `save_meal_feedback` —
that is a deliberate validation response, not an internal leak.

- [ ] **Step 6: Prove the leak is closed**

```bash
uv run pytest
```
Expected: **43 passed** (38 + 5 new).

```bash
uv run uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 &
sleep 8
echo "--- valid request still 200 ---"
curl -s -o /dev/null -w "%{http_code}\n" -X POST http://127.0.0.1:8000/generate-meal-plan \
  -H 'Content-Type: application/json' -d '{"craving":"pasta"}'
echo "--- validation error is 422, not 500 ---"
curl -s -o /dev/null -w "%{http_code}\n" -X POST http://127.0.0.1:8000/generate-meal-plan \
  -H 'Content-Type: application/json' -d '{"craving":"x"}'
kill %1
```
Expected: `200` then `422` (craving has `min_length=2`). Kill the server.

- [ ] **Step 7: Commit**

```bash
uv run ruff check . && uv run ruff format --check .
git status --short
git add backend/app/core/exceptions.py backend/tests/test_exceptions.py backend/app/main.py
git commit -F - <<'MSG'
feat(api): add typed domain exceptions and stop leaking internals

generate_meal_plan caught bare Exception and returned
detail=f"Meal plan generation failed: {exc}", putting the raw internal string in
the HTTP body and mapping every failure - provider outage, missing profile,
retrieval failure - onto a single 500. Spec section 6 item 8.

core/exceptions.py adds MealPlanningError plus ProfileNotFound (404),
RetrievalUnavailable (503) and NutritionProviderError (502), each carrying a safe
client_message. Registered handlers log the internal detail and return only the
safe message. A catch-all handler covers anything unexpected.

The bare try/except in generate_meal_plan is removed; the deliberate 400 in
save_meal_feedback stays, being a validation response rather than a leak.

Verified: 43 tests pass, including one asserting a credential-shaped internal
string never reaches client_message. Live checks return 200 for a valid request
and 422 for a validation failure.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
MSG
```

---

## Task 7: Dependency-injection container

Spec §6 item 4. This is what makes endpoints testable at all.

**Files:**
- Create: `backend/app/core/container.py`
- Modify: `backend/app/main.py`

**Interfaces:**
- Produces: `build_container(settings: AppSettings) -> Container` where `Container` is a
  dataclass with attributes `settings`, `user_profiles`, `meal_history`, `meal_feedback`,
  `meal_agent`, `nutrition_agent`, `supermarket_agent`, `calorie_agent`, `meal_planning_service`;
  plus `get_container(request: Request) -> Container` for use as `Depends(get_container)`.
  Task 8's routers depend on `get_container`.

- [ ] **Step 1: Write the module**

Create `backend/app/core/container.py`:

```python
"""Builds the application's agents and repositories once, for injection."""

from dataclasses import dataclass

from fastapi import Request

from ..agents.calorie_expenditure_agent import CalorieExpenditureAgent
from ..agents.meal_recommendation_agent import MealRecommendationAgent
from ..agents.nutrition_verification_agent import NutritionVerificationAgent
from ..agents.supermarket_agent import SupermarketAgent
from ..repositories.storage import (
    MealFeedbackRepository,
    MealPlanRepository,
    UserProfileRepository,
)
from ..services.meal_planning_service import MealPlanningService
from .config import AppSettings


@dataclass(frozen=True)
class Container:
    """The application's constructed collaborators."""

    settings: AppSettings
    user_profiles: UserProfileRepository
    meal_history: MealPlanRepository
    meal_feedback: MealFeedbackRepository
    meal_agent: MealRecommendationAgent
    nutrition_agent: NutritionVerificationAgent
    supermarket_agent: SupermarketAgent
    calorie_agent: CalorieExpenditureAgent
    meal_planning_service: MealPlanningService


def build_container(settings: AppSettings) -> Container:
    """Construct every collaborator once.

    Args:
        settings: Resolved application settings.

    Returns:
        A Container holding the built agents, repositories and service.
    """
    user_profiles = UserProfileRepository(settings.data_dir)
    meal_agent = MealRecommendationAgent(
        db_connection=user_profiles,
        gemini_api_key=settings.gemini_api_key,
        meal_corpus_path=settings.meal_corpus_path,
        enable_llm_adaptation=settings.enable_gemini_adaptation,
        rag_backend=settings.rag_backend,
        rag_embedding_cache_dir=settings.rag_embedding_cache_dir,
        rag_embedding_activation_size=settings.rag_embedding_activation_size,
    )
    nutrition_agent = NutritionVerificationAgent(
        usda_api_key=settings.usda_api_key,
        fatsecret_client_id=settings.fatsecret_client_id,
        fatsecret_client_secret=settings.fatsecret_client_secret,
    )
    supermarket_agent = SupermarketAgent(
        maps_api_key=settings.maps_api_key,
        inventory_api_key=settings.inventory_api_key,
    )
    calorie_agent = CalorieExpenditureAgent(
        model_path=settings.calorie_model_path,
        model_version=settings.calorie_model_version,
    )
    return Container(
        settings=settings,
        user_profiles=user_profiles,
        meal_history=MealPlanRepository(settings.data_dir),
        meal_feedback=MealFeedbackRepository(settings.data_dir),
        meal_agent=meal_agent,
        nutrition_agent=nutrition_agent,
        supermarket_agent=supermarket_agent,
        calorie_agent=calorie_agent,
        meal_planning_service=MealPlanningService(
            meal_agent=meal_agent,
            nutrition_agent=nutrition_agent,
            supermarket_agent=supermarket_agent,
            calorie_agent=calorie_agent,
            profile_repo=user_profiles,
        ),
    )


def get_container(request: Request) -> Container:
    """Return the container built during application startup.

    Args:
        request: The incoming request, whose app state holds the container.

    Returns:
        The application's Container.
    """
    return request.app.state.container
```

- [ ] **Step 2: Build the container in a lifespan handler**

In `backend/app/main.py`, replace the module-level construction (the block from
`user_profiles = UserProfileRepository(...)` through `meal_planning_service = MealPlanningService(...)`)
with a lifespan handler. Add imports:

```python
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from backend.app.core.container import Container, build_container, get_container
```

Then:

```python
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Build the container once at startup and expose it on app state."""
    app.state.container = build_container(settings)
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
```

Update every endpoint to take `container: Container = Depends(get_container)` and use
`container.meal_history`, `container.meal_planning_service` and so on instead of the module
globals. Import `Depends` from `fastapi`.

`/health` needs `container.calorie_agent`, `container.meal_agent` and `container.meal_history`
in place of the globals it reads today.

- [ ] **Step 3: Write endpoint tests using dependency overrides**

Create `backend/tests/test_api_endpoints.py`:

```python
"""TestClient coverage for every route, using dependency overrides."""

import pytest
from fastapi.testclient import TestClient

from backend.app.core.container import get_container
from backend.app.main import app


@pytest.fixture(name="client")
def _client() -> TestClient:
    """A client whose app has a real container built at startup."""
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_root_lists_endpoints(client: TestClient) -> None:
    body = client.get("/").json()
    assert body["status"] == "ok"
    assert "meal_plan" in body["links"]


def test_health_reports_the_calorie_model(client: TestClient) -> None:
    body = client.get("/health").json()
    assert body["status"] == "ok"
    assert body["services"]["calorie_model_configured"] is True


def test_generate_meal_plan_returns_every_section(client: TestClient) -> None:
    response = client.post("/generate-meal-plan", json={"craving": "high-protein burger"})
    assert response.status_code == 200
    body = response.json()
    for section in ("calorie_budget", "meal_plan", "nutrition", "shopping_list",
                    "reconciliation"):
        assert section in body


def test_generate_meal_plan_rejects_a_too_short_craving(client: TestClient) -> None:
    assert client.post("/generate-meal-plan", json={"craving": "x"}).status_code == 422


def test_predict_calorie_expenditure(client: TestClient) -> None:
    response = client.post(
        "/calorie-expenditure/predict",
        json={"age": 28, "sex": "male", "height_cm": 180, "weight_kg": 80},
    )
    assert response.status_code == 200
    assert response.json()["estimated_daily_expenditure_kcal"] > 0


def test_meal_feedback_requires_at_least_one_signal(client: TestClient) -> None:
    response = client.post(
        "/meal-feedback",
        json={"user_id": "user_123", "request_id": "abcdefgh", "meal_name": "Test Meal"},
    )
    assert response.status_code == 400


def test_meal_feedback_roundtrips(client: TestClient) -> None:
    saved = client.post(
        "/meal-feedback",
        json={"user_id": "pytest_user", "request_id": "abcdefgh",
              "meal_name": "Test Meal", "liked": True, "saved": True},
    )
    assert saved.status_code == 200
    listed = client.get("/meal-feedback/pytest_user").json()
    assert any(item["meal_name"] == "Test Meal" for item in listed["items"])
    savedonly = client.get("/saved-meals/pytest_user").json()
    assert all(item["saved"] for item in savedonly["items"])


def test_list_meal_plans_clamps_the_limit(client: TestClient) -> None:
    assert client.get("/meal-plans/user_123?limit=9999").json()["limit"] == 50


def test_container_override_is_honoured(client: TestClient) -> None:
    """Proves endpoints are injectable, which is the point of the container."""
    real = client.app.state.container

    class _Stub:
        def __getattr__(self, name: str) -> object:
            return getattr(real, name)

    app.dependency_overrides[get_container] = lambda: _Stub()
    assert client.get("/health").status_code == 200
    app.dependency_overrides.clear()
```

- [ ] **Step 4: Run**

```bash
uv run pytest
```
Expected: **52 passed**. `test_meal_feedback_roundtrips` writes to the real feedback store —
that is acceptable here because the repository appends and the file is gitignored. Confirm with
`git status --short` that `database/meal_feedback.json` is **not** shown as modified-and-tracked.

- [ ] **Step 5: Commit**

```bash
uv run ruff check . && uv run ruff format --check .
git status --short
git add backend/app/core/container.py backend/tests/test_api_endpoints.py backend/app/main.py
git commit -F - <<'MSG'
feat(core): build agents in a lifespan container and inject them

Agents and repositories were module-level singletons constructed at import time,
so importing main.py loaded the model artifact and built the retrieval index -
and no endpoint could be tested without doing both. Spec section 6 items 3 and 4.

core/container.py builds every collaborator once. A lifespan handler puts the
container on app.state, and get_container exposes it through Depends, so a test
can override the whole graph.

Adds the first endpoint tests in the repository: all 8 routes, happy and error
paths, including one that overrides the container to prove injection works.

Verified: 52 tests pass, ruff clean.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
MSG
```

---

## Task 8: Split `main.py` into routers

Spec §6 item 5.

**Files:**
- Create: `backend/app/api/__init__.py`, `backend/app/api/routes/__init__.py`, and
  `backend/app/api/routes/{health,meal_plans,calories,feedback}.py`
- Modify: `backend/app/main.py`

**Interfaces:**
- Consumes: `get_container` and `Container` from Task 7; the exception handlers from Task 6.
- Produces: four `APIRouter` objects named `router` in their modules.

- [ ] **Step 1: Create the packages**

```bash
mkdir -p backend/app/api/routes
printf '"""HTTP layer."""\n' > backend/app/api/__init__.py
printf '"""API route modules."""\n' > backend/app/api/routes/__init__.py
```

- [ ] **Step 2: Move the endpoints, unchanged**

Move each endpoint into its module, replacing the `@app.` decorator with `@router.`, where each
file starts with `router = APIRouter()`:

- `health.py` — `GET /` and `GET /health`
- `meal_plans.py` — `POST /generate-meal-plan` and `GET /meal-plans/{user_id}`
- `calories.py` — `POST /calorie-expenditure/predict`
- `feedback.py` — `POST /meal-feedback`, `GET /meal-feedback/{user_id}`, `GET /saved-meals/{user_id}`

**Copy the bodies verbatim.** Do not take the opportunity to improve them; any behaviour change
here is indistinguishable from a move in review. Each module imports what it needs
(`Container`, `get_container`, the request schemas, `run_in_threadpool`, `APIRouter`, `Depends`,
`HTTPException`, `Header`).

- [ ] **Step 3: Reduce `main.py` to app construction**

`backend/app/main.py` should end up as roughly:

```python
"""FastAPI application entry point."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routes import calories, feedback, health, meal_plans
from backend.app.core.config import AppSettings
from backend.app.core.container import build_container
from backend.app.core.exceptions import register_exception_handlers

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = AppSettings.from_env()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Build the container once at startup and expose it on app state."""
    app.state.container = build_container(settings)
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
register_exception_handlers(app)

app.include_router(health.router)
app.include_router(meal_plans.router)
app.include_router(calories.router)
app.include_router(feedback.router)


if __name__ == "__main__":
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
```

- [ ] **Step 4: Verify the route table is unchanged**

```bash
uv run python -c "
from backend.app.main import app
routes = sorted((r.path, tuple(sorted(r.methods - {'HEAD','OPTIONS'}))) for r in app.routes if hasattr(r,'methods'))
for p, m in routes: print(m, p)
print('count:', len(routes))
"
```
Expected: exactly 8 application routes (plus FastAPI's own `/docs`, `/openapi.json`, `/redoc`),
with the same paths and methods as before. Any difference means a move went wrong.

- [ ] **Step 5: Verify and commit**

```bash
uv run pytest
uv run ruff check . && uv run ruff format --check .
wc -l backend/app/main.py
git status --short
git add backend/app/api backend/app/main.py
git commit -F - <<'MSG'
refactor(api): split main.py into four routers

main.py held app construction, middleware, the lifespan handler and all eight
endpoints. Spec section 6 item 5.

The endpoints move verbatim into api/routes/{health,meal_plans,calories,feedback}.py
as APIRouters. main.py keeps only app construction, CORS, the lifespan handler,
exception-handler registration and router includes.

Bodies were copied without modification, so this commit is a pure move. The
route table was dumped before and after and is identical: same eight paths, same
methods.

Verified: 52 tests pass, ruff clean.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
MSG
```

---

## Task 9: Response models on every endpoint

Spec §6 item 6. `/docs` currently documents no response schemas.

**Files:**
- Create: `backend/app/schemas/responses.py`
- Modify: the four router modules

**Interfaces:**
- Consumes: `MealPlanResult` and `ReconciliationMetadata` (Tasks 1-2), `AgentMetadata` (Task 4).

- [ ] **Step 1: Write the failing test**

Create `backend/tests/test_response_contracts.py`:

```python
"""Every route must document a response schema and honour it."""

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app


@pytest.fixture(name="client")
def _client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client


def test_every_route_declares_a_response_model(client: TestClient) -> None:
    """No endpoint may fall back to an undocumented dict."""
    undocumented = [
        route.path
        for route in app.routes
        if hasattr(route, "methods") and getattr(route, "response_model", None) is None
        and route.path not in {"/openapi.json", "/docs", "/docs/oauth2-redirect", "/redoc"}
    ]
    assert undocumented == []


def test_openapi_documents_the_meal_plan_response(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()
    content = schema["paths"]["/generate-meal-plan"]["post"]["responses"]["200"]["content"]
    ref = content["application/json"]["schema"]["$ref"]
    assert ref.endswith("MealPlanResponse")


def test_meal_plan_response_still_carries_every_section(client: TestClient) -> None:
    body = client.post("/generate-meal-plan", json={"craving": "pasta"}).json()
    for section in ("status", "request_id", "generated_at", "request", "calorie_budget",
                    "meal_plan", "nutrition", "shopping_list", "reconciliation"):
        assert section in body
```

- [ ] **Step 2: Run to verify failure**

Run: `uv run pytest backend/tests/test_response_contracts.py`
Expected: FAIL — the first test lists all 8 paths as undocumented.

- [ ] **Step 3: Write the response models**

Create `backend/app/schemas/responses.py`:

```python
"""Response models, so /docs documents contracts instead of free-form dicts."""

from typing import Any

from pydantic import BaseModel

from ..agents.calorie_expenditure_agent import CalorieExpenditureResponse
from ..agents.meal_recommendation_agent import MealPlanPayload
from ..agents.nutrition_verification_agent import MealNutrition
from ..agents.supermarket_agent import SupermarketPayload
from ..services.meal_planning_service import ReconciliationMetadata


class RootResponse(BaseModel):
    """Service banner and endpoint links."""

    name: str
    status: str
    message: str
    links: dict[str, str]


class HealthResponse(BaseModel):
    """Service health and external provider configuration."""

    status: str
    environment: str
    services: dict[str, Any]


class MealPlanResponse(BaseModel):
    """A generated meal plan with its verification and reconciliation metadata."""

    status: str
    request_id: str
    generated_at: str
    request: dict[str, Any]
    calorie_budget: CalorieExpenditureResponse
    meal_plan: MealPlanPayload
    nutrition: MealNutrition
    shopping_list: SupermarketPayload
    reconciliation: ReconciliationMetadata | None = None


class MealPlanListResponse(BaseModel):
    """Stored meal plans for one user."""

    user_id: str
    limit: int
    items: list[dict[str, Any]]


class FeedbackResponse(BaseModel):
    """The persisted feedback record."""

    status: str
    item: dict[str, Any]


class FeedbackListResponse(BaseModel):
    """Feedback or saved meals for one user."""

    user_id: str
    limit: int
    items: list[dict[str, Any]]
```

`items` stays `list[dict[str, Any]]` deliberately: history records are whole stored responses
whose shape has changed across versions, and typing them strictly would make old records
unreadable. Note this in the module docstring.

- [ ] **Step 4: Attach the models**

Add `response_model=` to each route decorator:

| Route | Model |
| --- | --- |
| `GET /` | `RootResponse` |
| `GET /health` | `HealthResponse` |
| `POST /generate-meal-plan` | `MealPlanResponse` |
| `GET /meal-plans/{user_id}` | `MealPlanListResponse` |
| `POST /calorie-expenditure/predict` | `CalorieExpenditureResponse` |
| `POST /meal-feedback` | `FeedbackResponse` |
| `GET /meal-feedback/{user_id}` | `FeedbackListResponse` |
| `GET /saved-meals/{user_id}` | `FeedbackListResponse` |

Also change each handler's return annotation to the model, and return the model where the
handler currently builds a dict. For `/calorie-expenditure/predict`, return the
`CalorieExpenditureResponse` directly rather than `response.model_dump()`.

- [ ] **Step 5: Run everything**

```bash
uv run pytest
```
Expected: **55 passed**.

- [ ] **Step 6: Confirm `/docs` now documents responses**

```bash
uv run uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 &
sleep 8
curl -s http://127.0.0.1:8000/openapi.json | uv run python -c "
import json,sys
s=json.load(sys.stdin)
for path, ops in sorted(s['paths'].items()):
    for verb, op in ops.items():
        ref = op['responses']['200']['content']['application/json']['schema'].get('\$ref','NONE')
        print(f'{verb.upper():5} {path:34} {ref.split(\"/\")[-1]}')
"
kill %1
```
Expected: every one of the 8 rows names a model; none says `NONE`.

- [ ] **Step 7: Commit**

```bash
uv run ruff check . && uv run ruff format --check .
git status --short
git add backend/app/schemas/responses.py backend/tests/test_response_contracts.py backend/app/api/routes
git commit -F - <<'MSG'
feat(schemas): document and enforce a response model on every endpoint

All eight routes returned dict[str, Any], so /docs showed no response schemas
and nothing enforced the contract. Spec section 6 item 6.

schemas/responses.py adds a model per endpoint and each route now declares
response_model. History and feedback items stay dict[str, Any] on purpose:
stored records are whole responses from earlier versions, and typing them
strictly would make old rows unreadable. The module docstring says so.

Verified: 55 tests pass, including one that fails if any route ever ships
without a response_model again, and an OpenAPI dump showing all eight routes
naming a schema.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
MSG
```

---

## Phase 1 Exit Gate

Per spec §6: done when `/generate-meal-plan` demonstrably uses the model's calorie budget, the
response includes reconciliation metadata, `/docs` shows full response schemas, and a provider
failure returns a non-500 status with no internal detail in the body.

- [ ] `uv run pytest` → **55 passed**, no test deleted or weakened
- [ ] `uv run ruff check .` and `uv run ruff format --check .` → clean
- [ ] A live `POST /generate-meal-plan` returns `calorie_budget.model_version` =
      `hist_gradient_boosting_deep_v0.1.0`, and `meal_plan.user_context.caloric_target`
      equals `calorie_budget.meal_calorie_budget_kcal`
- [ ] That response carries a `reconciliation` object with `tolerance: 0.15`
- [ ] `/openapi.json` names a response schema for all 8 routes
- [ ] A validation failure returns 422; no response body contains a raw exception string
- [ ] `backend/app/main.py` is under 60 lines and contains no endpoint
- [ ] `grep -rn "calculate_bmr\|predict_user_preferences" backend/app/` → no output
- [ ] `git status --short` clean; no `.env` or `database/*.json` staged
- [ ] Update `docs/2_architecture.md`'s divergence note: retire the orchestrator, DI-container,
      step-3 and step-6 claims **individually**. The step-8 embeddings claim must **remain** —
      Phase 1 does not deliver it. (Codex review, 2026-09-11.)
- [ ] Append a Phase 1 entry to `docs/5_agent_log.md`; tick this checklist
