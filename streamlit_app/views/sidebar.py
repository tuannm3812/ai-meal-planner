"""The sidebar: run mode, API health, optional keys and the user profile."""

from typing import Any

import streamlit as st
from api import parse_extra_items, render_api_error, request_json
from config import AppConfig, get_secret
from demo import local_demo_request

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


def render_sidebar() -> AppConfig:
    """Render the sidebar controls and resolve them into the app's configuration.

    The health check calls ``local_demo_request`` and ``request_json`` directly
    rather than through the tabs' request callable, because that callable is built
    from the config this function is still assembling.

    Returns:
        Every sidebar value the tabs consume, plus the derived health conditions
        and demo-mode profile.
    """
    # Resolved per call, not at import: app.py re-read it on every script rerun.
    default_api_base_url = get_secret("API_BASE_URL", "http://localhost:8000")

    with st.sidebar:
        st.subheader("Run Mode")
        use_demo_mode = st.toggle(
            "Self-contained Streamlit demo",
            value=get_secret("STREAMLIT_DEMO_MODE", "0") == "1",
            help="Run the demo directly inside Streamlit without calling FastAPI.",
        )
        api_base_url = default_api_base_url
        if use_demo_mode:
            st.caption(
                "Using local agents inside Streamlit. FastAPI is not required for this demo."
            )
        else:
            st.subheader("API")
            api_base_url = st.text_input("Base URL", value=default_api_base_url)
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
    return AppConfig(
        use_demo_mode=use_demo_mode,
        api_base_url=api_base_url,
        gemini_api_key=gemini_api_key,
        user_id=user_id,
        profile=streamlit_profile,
        health_conditions=selected_health_conditions,
        dietary_preferences=dietary_preferences,
        age=age,
        sex=sex,
        height_cm=height_cm,
        weight_kg=weight_kg,
        activity_multiplier=activity_multiplier,
        duration_minutes=duration_minutes,
        heart_rate_bpm=heart_rate_bpm,
        body_temp_c=body_temp_c,
        goal=goal,
    )
