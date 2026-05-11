import os
from pathlib import Path
import tomllib
from typing import Any

import requests
import streamlit as st


st.set_page_config(page_title="AI Meal Planner", page_icon="A", layout="wide")


def get_secret(name: str, default: str = "") -> str:
    env_value = os.getenv(name)
    if env_value:
        return env_value

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


st.title("AI Meal Planner")

with st.sidebar:
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
                    'GEMINI_API_KEY = "optional-key-for-future-direct-streamlit-mode"',
                    "```",
                ]
            )
        )

    try:
        health_payload = request_json("GET", api_base_url, "/health")
        st.success("API online")
        with st.expander("Health payload"):
            st.json(health_payload)
    except Exception as exc:
        st.warning("API offline or unreachable")
        with st.expander("Connection details"):
            render_api_error(exc)

    st.divider()
    st.subheader("AI Keys")
    gemini_key_source = "configured on API" if health_payload.get("services", {}).get("gemini_configured") else "not configured"
    st.caption(f"Gemini status: {gemini_key_source}")
    gemini_api_key = st.text_input(
        "Gemini API key",
        value=get_secret("GEMINI_API_KEY"),
        type="password",
        help=(
            "For deployed testing, set this in Streamlit secrets. "
            "The current FastAPI backend reads Gemini from backend/.env at startup."
        ),
    )
    if gemini_api_key and not health_payload.get("services", {}).get("gemini_configured"):
        st.info("The UI captured a key, but the API must also be configured or restarted with GEMINI_API_KEY.")

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
            try:
                with st.spinner("Planning meal..."):
                    meal_result = request_json(
                        "POST",
                        api_base_url,
                        "/generate-meal-plan",
                        {
                            "user_id": user_id,
                            "craving": craving,
                            "location": location,
                            "health_conditions": selected_health_conditions,
                            "dietary_preferences": dietary_preferences,
                        },
                        headers={"X-Gemini-API-Key": gemini_api_key} if gemini_api_key else None,
                    )

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
                calorie_result = request_json(
                    "POST",
                    api_base_url,
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
            history_result = request_json(
                "GET",
                api_base_url,
                f"/meal-plans/{user_id}?limit={history_limit}",
            )
            items = history_result.get("items", [])
            st.metric("Records", len(items))
            st.json(history_result)
        except Exception as exc:
            render_api_error(exc)
