import os
from pathlib import Path
import sys
import tomllib
from typing import Any
from datetime import UTC, datetime
from uuid import uuid4

import requests
import streamlit as st


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

st.set_page_config(page_title="AI Meal Planner", page_icon="A", layout="wide")


def get_secret(name: str, default: str = "") -> str:
    env_value = os.getenv(name)
    if env_value:
        return env_value

    try:
        value = st.secrets.get(name)
        if value:
            return str(value)
    except Exception:
        pass

    local_secrets_path = Path(".streamlit") / "secrets.toml"
    if local_secrets_path.exists():
        try:
            secrets = tomllib.loads(local_secrets_path.read_text(encoding="utf-8"))
            value = secrets.get(name)
            if value:
                return str(value)
        except tomllib.TOMLDecodeError:
            return default

    return default


DEFAULT_API_BASE_URL = get_secret("API_BASE_URL", "http://localhost:8000")
DEMO_DATA_DIR = Path("/tmp/ai_meal_planner") if os.getenv("STREAMLIT_SHARING") else Path("database")
DEMO_DATA_DIR.mkdir(parents=True, exist_ok=True)
COMMON_HEALTH_CONDITIONS = [
    "None",
    "Diabetes",
    "Hypertension",
    "High cholesterol",
    "Kidney disease",
    "Heart disease",
    "Pregnancy",
    "Food allergy",
    "Gluten intolerance",
    "Lactose intolerance",
]
DIETARY_PREFERENCES = [
    "High protein",
    "Low carb",
    "Low sodium",
    "Dairy free",
    "Gluten free",
    "Vegetarian",
    "Vegan",
    "Halal",
    "Kosher",
]
ACTIVITY_LEVELS = {
    "Sedentary - little or no exercise": 1.2,
    "Light - exercise 1-3 days/week": 1.375,
    "Moderate - exercise 3-5 days/week": 1.55,
    "Very active - hard exercise 6-7 days/week": 1.725,
    "Extra active - physical job or athlete": 1.9,
}


def request_json(
    method: str,
    base_url: str,
    path: str,
    payload: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> dict[str, Any]:
    url = f"{base_url.rstrip('/')}{path}"
    response = requests.request(method, url, json=payload, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()


def render_api_error(exc: Exception) -> None:
    if isinstance(exc, requests.HTTPError):
        response = exc.response
        try:
            detail = response.json()
        except ValueError:
            detail = response.text
        st.error(f"API request failed with status {response.status_code}.")
        st.code(detail, language="json")
        return

    if isinstance(exc, requests.ConnectionError):
        st.error("Could not connect to the API. Start FastAPI on http://localhost:8000 first.")
        return

    st.error(f"Unexpected API error: {exc}")


def parse_extra_items(raw_value: str) -> list[str]:
    return [item.strip() for item in raw_value.split(",") if item.strip()]


def is_meal_like_input(value: str) -> bool:
    normalized_value = value.strip().lower()
    polite_only = {
        "thank you",
        "thanks",
        "hello",
        "hi",
        "hey",
        "ok",
        "okay",
        "test",
    }
    if normalized_value in polite_only:
        return False
    return len(normalized_value) >= 3


class StreamlitUserProfileRepository:
    def __init__(
        self,
        age: int,
        sex: str,
        height_cm: float,
        weight_kg: float,
        activity_multiplier: float,
        dietary_restrictions: list[str],
    ):
        self.profile = {
            "age": age,
            "gender": "m" if sex.lower().startswith("male") else "f",
            "height": height_cm,
            "weight": weight_kg,
            "workout_level": activity_multiplier,
            "dietary_restrictions": dietary_restrictions,
        }

    def fetch_user_profile(self, user_id: str) -> dict[str, Any]:
        return self.profile


def local_demo_request(
    path: str,
    payload: dict[str, Any] | None,
    profile: dict[str, Any],
    api_key: str = "",
) -> dict[str, Any]:
    payload = payload or {}
    if path == "/health":
        return {
            "status": "ok",
            "environment": "streamlit_demo",
            "services": {
                "mode": "self_contained_streamlit",
                "gemini_configured": bool(api_key),
                "usda_configured": bool(get_secret("USDA_API_KEY")),
                "rag_backend": "lazy_loaded_local",
            },
        }

    try:
        from backend.app.agents.nutrition_verification_agent import NutritionVerificationAgent
        from backend.app.agents.supermarket_agent import SupermarketAgent
        from backend.app.repositories.storage import MealFeedbackRepository, MealPlanRepository
    except ImportError as exc:
        raise RuntimeError(f"Local demo mode cannot import backend storage modules: {exc}") from exc

    user_repository = StreamlitUserProfileRepository(
        age=int(profile["age"]),
        sex=str(profile["sex"]),
        height_cm=float(profile["height_cm"]),
        weight_kg=float(profile["weight_kg"]),
        activity_multiplier=float(profile["activity_multiplier"]),
        dietary_restrictions=profile["dietary_restrictions"],
    )

    if path == "/generate-meal-plan":
        try:
            from backend.app.agents.meal_recommendation_agent import MealRecommendationAgent
        except ImportError as exc:
            raise RuntimeError(f"Local demo mode cannot import meal agent: {exc}") from exc

        request_id = str(uuid4())
        meal_agent = MealRecommendationAgent(
            db_connection=user_repository,
            gemini_api_key=api_key or None,
            meal_corpus_path=Path("data/meal_corpus/meals.json"),
            enable_llm_adaptation=get_secret("ENABLE_GEMINI_ADAPTATION", "0") == "1",
        )
        nutrition_agent = NutritionVerificationAgent(
            usda_api_key=get_secret("USDA_API_KEY") or None,
            fatsecret_client_id=get_secret("FATSECRET_CLIENT_ID") or None,
            fatsecret_client_secret=get_secret("FATSECRET_CLIENT_SECRET") or None,
        )
        supermarket_agent = SupermarketAgent()
        meal_payload = meal_agent.generate_meal_payload(
            craving=payload["craving"],
            user_id=payload.get("user_id", "user_123"),
            health_conditions=payload.get("health_conditions", []),
            dietary_preferences=payload.get("dietary_preferences", []),
        )
        nutrition_payload = nutrition_agent.calculate_meal_macros(
            meal_payload.meal_definition.ingredients
        )
        shopping_payload = supermarket_agent.generate_shopping_list(
            meal_payload.meal_definition.ingredients,
            payload.get("location", "Earlwood, NSW"),
        )
        response = {
            "status": "success",
            "request_id": request_id,
            "generated_at": datetime.now(UTC).isoformat(),
            "request": payload,
            "meal_plan": meal_payload.model_dump(),
            "nutrition": nutrition_payload.model_dump(),
            "shopping_list": shopping_payload.model_dump(),
        }
        MealPlanRepository(DEMO_DATA_DIR).save(response)
        return response

    if path == "/calorie-expenditure/predict":
        try:
            from backend.app.agents.calorie_expenditure_agent import (
                CalorieExpenditureAgent,
                CalorieExpenditureRequest,
            )
        except ImportError as exc:
            raise RuntimeError(f"Local demo mode cannot import calorie agent: {exc}") from exc

        agent = CalorieExpenditureAgent(
            model_path=Path("models/calorie_expenditure/calorie_expenditure_model.joblib"),
            model_version="hist_gradient_boosting_deep_v0.1.0",
        )
        request = CalorieExpenditureRequest.model_validate(payload)
        return agent.predict(request).model_dump()

    if path == "/meal-feedback":
        record = MealFeedbackRepository(DEMO_DATA_DIR).save(payload)
        return {"status": "success", "item": record}

    if path.startswith("/meal-plans/"):
        user_id = path.split("/", 2)[2].split("?", 1)[0]
        return {
            "user_id": user_id,
            "items": MealPlanRepository(DEMO_DATA_DIR).list_for_user(user_id=user_id),
        }

    if path.startswith("/saved-meals/"):
        user_id = path.split("/", 2)[2].split("?", 1)[0]
        return {
            "user_id": user_id,
            "items": MealFeedbackRepository(DEMO_DATA_DIR).list_for_user(
                user_id=user_id,
                saved_only=True,
            ),
        }

    raise ValueError(f"Unsupported local demo path: {path}")


st.title("AI Meal Planner")

if "latest_meal_result" not in st.session_state:
    st.session_state.latest_meal_result = None

with st.sidebar:
    st.subheader("Run Mode")
    use_demo_mode = st.toggle(
        "Self-contained Streamlit demo",
        value=get_secret("STREAMLIT_DEMO_MODE", "0") == "1",
        help="Run the demo directly inside Streamlit without calling FastAPI.",
    )
    api_base_url = DEFAULT_API_BASE_URL
    if use_demo_mode:
        st.caption("Using local agents inside Streamlit. FastAPI is not required for this demo.")
    else:
        st.subheader("API")
        api_base_url = st.text_input("Base URL", value=DEFAULT_API_BASE_URL)
    health_payload: dict[str, Any] = {}
    with st.expander("Deployment settings"):
        st.markdown(
            "\n".join(
                [
                    "**Streamlit Cloud**",
                    "- Repository: `tuannm3812/ai-meal-planner`",
                    "- Branch: `main`",
                    "- Main file path: `streamlit_app/app.py`",
                    "- App URL: choose an available slug such as `tuannm-ai-meal-planner`",
                    "",
                    "**Secrets**",
                    "```toml",
                    'API_BASE_URL = "https://your-backend-url"',
                    'STREAMLIT_DEMO_MODE = "1"',
                    'GEMINI_API_KEY = "optional-key-for-final-explanations"',
                    "```",
                ]
            )
        )

    try:
        if use_demo_mode:
            health_payload = local_demo_request(
                "/health",
                None,
                {
                    "age": 28,
                    "sex": "male",
                    "height_cm": 180.0,
                    "weight_kg": 80.0,
                    "activity_multiplier": 1.55,
                    "dietary_restrictions": ["dairy-free", "high-protein"],
                },
                get_secret("GEMINI_API_KEY"),
            )
            st.success("Demo mode ready")
        else:
            health_payload = request_json("GET", api_base_url, "/health")
            st.success("API online")
        with st.expander("Health payload"):
            st.json(health_payload)
    except Exception as exc:
        st.warning("API offline, unreachable, or demo mode unavailable")
        with st.expander("Connection details"):
            render_api_error(exc)

    gemini_api_key = get_secret("GEMINI_API_KEY")
    with st.expander("Optional AI keys"):
        gemini_key_source = (
            "configured"
            if health_payload.get("services", {}).get("gemini_configured") or gemini_api_key
            else "not configured"
        )
        st.caption(f"Gemini status: {gemini_key_source}")
        gemini_api_key = st.text_input(
            "Gemini API key",
            value=gemini_api_key,
            type="password",
            help="Optional. Gemini is only used for final explanation when enabled.",
        )

    st.divider()
    st.subheader("Profile")
    user_id = st.text_input("User ID", value="user_123")
    age = st.number_input("Age", min_value=1, max_value=120, value=28)
    sex = st.selectbox("Sex", options=["male", "female"], index=0)
    height_cm = st.number_input("Height (cm)", min_value=80.0, max_value=260.0, value=180.0)
    weight_kg = st.number_input("Weight (kg)", min_value=20.0, max_value=350.0, value=80.0)
    activity_level = st.selectbox(
        "Activity level",
        options=list(ACTIVITY_LEVELS),
        index=2,
        help=(
            "Used to estimate daily calorie expenditure from BMR. "
            "Moderate activity is 1.55, meaning roughly 55% above resting needs."
        ),
    )
    activity_multiplier = ACTIVITY_LEVELS[activity_level]
    with st.expander("Advanced activity multiplier"):
        activity_multiplier = st.slider(
            "Manual multiplier",
            1.0,
            2.5,
            activity_multiplier,
            0.025,
            help=(
                "Typical values: 1.2 sedentary, 1.375 light, 1.55 moderate, "
                "1.725 very active, 1.9 extra active."
            ),
        )
    duration_minutes = st.number_input("Exercise duration (min)", min_value=1.0, max_value=600.0, value=30.0)
    heart_rate_bpm = st.number_input("Heart rate (bpm)", min_value=20.0, max_value=240.0, value=100.0)
    body_temp_c = st.number_input("Body temp (C)", min_value=30.0, max_value=45.0, value=40.0)
    goal = st.selectbox("Goal", options=["maintain", "weight_loss", "muscle_gain"], index=0)
    health_condition_options = st.multiselect(
        "Health conditions",
        options=COMMON_HEALTH_CONDITIONS,
        default=["None"],
        help="Choose known constraints. Use extra notes for anything not listed.",
    )
    extra_health_conditions = st.text_input("Other health notes", value="")
    dietary_preferences = st.multiselect("Dietary preferences", options=DIETARY_PREFERENCES)

selected_health_conditions = [
    condition for condition in health_condition_options if condition != "None"
] + parse_extra_items(extra_health_conditions)
streamlit_profile = {
    "age": age,
    "sex": sex,
    "height_cm": height_cm,
    "weight_kg": weight_kg,
    "activity_multiplier": activity_multiplier,
    "dietary_restrictions": [
        preference.lower().replace(" ", "-")
        for preference in dietary_preferences
        if preference.lower() in {"dairy free", "gluten free", "high protein"}
    ],
}


def call_demo_or_api(
    method: str,
    path: str,
    payload: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> dict[str, Any]:
    if use_demo_mode:
        return local_demo_request(
            path=path,
            payload=payload,
            profile=streamlit_profile,
            api_key=gemini_api_key,
        )
    return request_json(method, api_base_url, path, payload, headers)

meal_tab, calorie_tab, history_tab = st.tabs(["Meal Plan", "Calories", "History"])

with meal_tab:
    left_col, right_col = st.columns([0.8, 1.2])
    with left_col:
        st.subheader("Request")
        craving = st.text_input("Craving or meal goal", value="high-protein burger")
        location = st.text_input("Location", value="Earlwood, NSW")
        generate_meal = st.button("Generate meal", type="primary")

    with right_col:
        st.subheader("Response")
        if generate_meal:
            if not is_meal_like_input(craving):
                st.warning("Enter a meal craving or goal, for example `salmon bowl`, `fried rice`, or `high-protein burger`.")
            else:
                try:
                    with st.spinner("Planning meal..."):
                        meal_result = call_demo_or_api(
                            "POST",
                            "/generate-meal-plan",
                            {
                                "user_id": user_id,
                                "craving": craving,
                                "location": location,
                                "health_conditions": selected_health_conditions,
                                "dietary_preferences": dietary_preferences,
                            },
                            {"X-Gemini-API-Key": gemini_api_key} if gemini_api_key else None,
                        )

                    st.session_state.latest_meal_result = meal_result
                    meal_definition = meal_result.get("meal_plan", {}).get("meal_definition", {})
                    nutrition = meal_result.get("nutrition", {})
                    shopping_list = meal_result.get("shopping_list", {})
                    metadata = meal_result.get("meal_plan", {}).get("metadata", {})
                    retrieval = meal_result.get("meal_plan", {}).get("retrieval")

                    st.success(meal_definition.get("structured_meal_name", "Meal generated"))
                    st.caption(
                        f"Source: {metadata.get('source', 'unknown')} | "
                        f"Confidence: {metadata.get('confidence', 0):.0%}"
                    )
                    if metadata.get("explanation"):
                        st.info(metadata["explanation"])
                    metric_cols = st.columns(4)
                    metric_cols[0].metric("Calories", nutrition.get("total_calories", 0))
                    metric_cols[1].metric("Protein", f"{nutrition.get('total_protein', 0)} g")
                    metric_cols[2].metric("Carbs", f"{nutrition.get('total_carbs', 0)} g")
                    metric_cols[3].metric("Fat", f"{nutrition.get('total_fat', 0)} g")

                    with st.expander("Ingredients", expanded=True):
                        st.dataframe(meal_definition.get("ingredients", []), use_container_width=True)
                    if metadata.get("warnings"):
                        with st.expander("Retrieval and generation notes", expanded=True):
                            for warning in metadata["warnings"]:
                                st.write(f"- {warning}")
                    if retrieval:
                        with st.expander("RAG retrieval contract", expanded=True):
                            st.json(retrieval)
                    with st.expander("Nutrition details"):
                        st.json(nutrition)
                    with st.expander("Shopping list"):
                        st.json(shopping_list)
                    with st.expander("Raw API response"):
                        st.json(meal_result)
                except Exception as exc:
                    render_api_error(exc)
        else:
            st.info("Submit a craving to call `/generate-meal-plan`.")

        latest_meal_result = st.session_state.latest_meal_result
        if latest_meal_result:
            meal_definition = latest_meal_result.get("meal_plan", {}).get("meal_definition", {})
            retrieval = latest_meal_result.get("meal_plan", {}).get("retrieval") or {}
            st.divider()
            st.subheader("Feedback")
            feedback_cols = st.columns([0.5, 0.5, 0.7, 1.2])
            liked_label = feedback_cols[0].selectbox(
                "Like",
                options=["No signal", "Like", "Dislike"],
            )
            rating = feedback_cols[1].selectbox(
                "Rating",
                options=["No rating", 1, 2, 3, 4, 5],
                index=0,
            )
            saved = feedback_cols[2].checkbox("Save meal")
            notes = feedback_cols[3].text_input("Notes", value="")
            if st.button("Submit feedback"):
                liked = None
                if liked_label == "Like":
                    liked = True
                elif liked_label == "Dislike":
                    liked = False
                try:
                    feedback_result = call_demo_or_api(
                        "POST",
                        "/meal-feedback",
                        {
                            "user_id": user_id,
                            "request_id": latest_meal_result.get("request_id", ""),
                            "meal_id": retrieval.get("selected_meal_id"),
                            "meal_name": meal_definition.get("structured_meal_name", "Unknown meal"),
                            "liked": liked,
                            "rating": rating if isinstance(rating, int) else None,
                            "saved": saved,
                            "notes": notes or None,
                        },
                    )
                    st.success("Feedback saved")
                    st.json(feedback_result)
                except Exception as exc:
                    render_api_error(exc)

with calorie_tab:
    st.subheader("Calorie Expenditure")
    calorie_payload = {
        "age": age,
        "sex": sex,
        "height_cm": height_cm,
        "weight_kg": weight_kg,
        "activity_multiplier": activity_multiplier,
        "duration_minutes": duration_minutes,
        "heart_rate_bpm": heart_rate_bpm,
        "body_temp_c": body_temp_c,
        "goal": goal,
        "health_conditions": selected_health_conditions,
    }

    st.caption("This calls `/calorie-expenditure/predict` using the promoted Kaggle model artifact.")
    if selected_health_conditions:
        st.warning(
            "Health conditions are passed as constraints only. This app does not provide medical advice."
        )
    if dietary_preferences:
        st.info(f"Dietary preferences selected for upcoming recommendation work: {', '.join(dietary_preferences)}")
    with st.expander("Request payload"):
        st.json(calorie_payload)

    if st.button("Predict expenditure", type="primary"):
        try:
            with st.spinner("Predicting calorie budget..."):
                calorie_result = call_demo_or_api(
                    "POST",
                    "/calorie-expenditure/predict",
                    calorie_payload,
                )
            metric_cols = st.columns(3)
            metric_cols[0].metric(
                "Daily expenditure",
                f"{calorie_result['estimated_daily_expenditure_kcal']:,.0f} kcal",
            )
            metric_cols[1].metric(
                "Meal budget",
                f"{calorie_result['meal_calorie_budget_kcal']:,.0f} kcal",
            )
            metric_cols[2].metric("Confidence", f"{calorie_result['confidence']:.0%}")
            st.json(calorie_result)
        except Exception as exc:
            render_api_error(exc)

with history_tab:
    st.subheader("Meal History")
    history_limit = st.slider("Limit", 1, 50, 10)
    if st.button("Load history"):
        try:
            history_result = call_demo_or_api(
                "GET",
                f"/meal-plans/{user_id}?limit={history_limit}",
            )
            items = history_result.get("items", [])
            st.metric("Records", len(items))
            st.json(history_result)
        except Exception as exc:
            render_api_error(exc)

    st.divider()
    st.subheader("Saved Meals")
    if st.button("Load saved meals"):
        try:
            saved_result = call_demo_or_api(
                "GET",
                f"/saved-meals/{user_id}?limit={history_limit}",
            )
            st.metric("Saved", len(saved_result.get("items", [])))
            st.json(saved_result)
        except Exception as exc:
            render_api_error(exc)
