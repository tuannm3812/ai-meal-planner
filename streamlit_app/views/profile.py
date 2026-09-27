"""The sidebar's Profile section: body metrics, activity, goal and dietary needs."""

from typing import Any

import streamlit as st
from api import parse_extra_items

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


def render_profile() -> dict[str, Any]:
    """Render the Profile controls into the current container and resolve them.

    Called by ``render_sidebar`` inside its ``with st.sidebar:`` block, so the
    widgets land in the sidebar in the same position and order as before.

    Returns:
        The profile-derived ``AppConfig`` fields, keyed by field name: ``user_id``,
        ``profile``, ``health_conditions``, ``dietary_preferences``, ``age``, ``sex``,
        ``height_cm``, ``weight_kg``, ``activity_multiplier``, ``duration_minutes``,
        ``heart_rate_bpm``, ``body_temp_c`` and ``goal``.
    """
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
    return {
        "user_id": user_id,
        "profile": streamlit_profile,
        "health_conditions": selected_health_conditions,
        "dietary_preferences": dietary_preferences,
        "age": age,
        "sex": sex,
        "height_cm": height_cm,
        "weight_kg": weight_kg,
        "activity_multiplier": activity_multiplier,
        "duration_minutes": duration_minutes,
        "heart_rate_bpm": heart_rate_bpm,
        "body_temp_c": body_temp_c,
        "goal": goal,
    }
