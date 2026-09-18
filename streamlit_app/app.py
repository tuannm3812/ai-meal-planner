import sys
from pathlib import Path
from typing import Any

import streamlit as st
from api import parse_extra_items, render_api_error, request_json
from config import get_secret
from demo import local_demo_request

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

st.set_page_config(page_title="AI Meal Planner", page_icon="A", layout="wide")

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
        services = health_payload.get("services", {})
        status_lines = [
            ("Gemini", services.get("gemini_configured")),
            ("USDA", services.get("usda_configured")),
            ("FatSecret", services.get("fatsecret_configured")),
            ("Calorie model", services.get("calorie_model_configured")),
        ]
        for label, configured in status_lines:
            if configured:
                st.success(f"{label}: configured", icon="✅")
            else:
                st.warning(f"{label}: not configured", icon="⚠️")
        rag_backend = services.get("rag_backend")
        if rag_backend:
            st.caption(f"RAG backend: `{rag_backend}`")
        with st.expander("Full health payload"):
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
    duration_minutes = st.number_input(
        "Exercise duration (min)", min_value=1.0, max_value=600.0, value=30.0
    )
    heart_rate_bpm = st.number_input(
        "Heart rate (bpm)", min_value=20.0, max_value=240.0, value=100.0
    )
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
                st.warning(
                    "Enter a meal craving or goal, for example `salmon bowl`, "
                    "`fried rice`, or `high-protein burger`."
                )
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
                        st.dataframe(
                            meal_definition.get("ingredients", []), use_container_width=True
                        )
                    if metadata.get("warnings"):
                        with st.expander("Retrieval and generation notes", expanded=True):
                            for warning in metadata["warnings"]:
                                st.write(f"- {warning}")
                    if retrieval:
                        with st.expander("RAG retrieval contract", expanded=True):
                            st.json(retrieval)
                    with st.expander("Nutrition details"):
                        st.json(nutrition)
                    with st.expander("Shopping list", expanded=True):
                        shopping_items = shopping_list.get("shopping_list", [])
                        if shopping_items:
                            st.dataframe(shopping_items, use_container_width=True)
                            st.metric(
                                "Estimated total",
                                f"${shopping_list.get('total_estimated_cost', 0):,.2f}",
                            )
                        else:
                            st.caption("No shopping list items returned.")
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
                            "meal_name": meal_definition.get(
                                "structured_meal_name", "Unknown meal"
                            ),
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

    st.caption(
        "This calls `/calorie-expenditure/predict` using the promoted Kaggle model artifact."
    )
    if selected_health_conditions:
        st.warning(
            "Health conditions are passed as constraints only. This app does "
            "not provide medical advice."
        )
    if dietary_preferences:
        st.info(
            "Dietary preferences selected for upcoming recommendation work: "
            f"{', '.join(dietary_preferences)}"
        )
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
            with st.spinner("Loading meal history..."):
                history_result = call_demo_or_api(
                    "GET",
                    f"/meal-plans/{user_id}?limit={history_limit}",
                )
            items = history_result.get("items", [])
            st.metric("Records", len(items))
            if items:
                st.json(history_result)
            else:
                st.info("No meal history yet — generate a plan first.")
        except Exception as exc:
            render_api_error(exc)

    st.divider()
    st.subheader("Saved Meals")
    if st.button("Load saved meals"):
        try:
            with st.spinner("Loading saved meals..."):
                saved_result = call_demo_or_api(
                    "GET",
                    f"/saved-meals/{user_id}?limit={history_limit}",
                )
            items = saved_result.get("items", [])
            st.metric("Saved", len(items))
            if items:
                st.json(saved_result)
            else:
                st.info("No saved meals yet — mark a meal as saved from the Meal Plan tab.")
        except Exception as exc:
            render_api_error(exc)
