import os
from typing import Any

import requests
import streamlit as st


API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def post_json(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    response = requests.post(f"{API_BASE_URL}{path}", json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


st.set_page_config(page_title="AI Meal Planner", page_icon="A", layout="wide")
st.title("AI Meal Planner")

with st.sidebar:
    st.subheader("Profile")
    user_id = st.text_input("User ID", value="user_123")
    age = st.number_input("Age", min_value=1, max_value=120, value=28)
    sex = st.selectbox("Sex", options=["male", "female"], index=0)
    height_cm = st.number_input("Height (cm)", min_value=80.0, max_value=260.0, value=180.0)
    weight_kg = st.number_input("Weight (kg)", min_value=20.0, max_value=350.0, value=80.0)
    activity_multiplier = st.slider("Activity multiplier", 1.0, 2.5, 1.55, 0.05)
    goal = st.selectbox("Goal", options=["maintain", "weight_loss", "muscle_gain"], index=0)
    health_conditions = st.text_input("Health conditions", value="")

meal_col, calorie_col = st.columns([1.2, 1])

with meal_col:
    st.subheader("Generate Meal Plan")
    craving = st.text_input("Craving or meal goal", value="high-protein burger")
    location = st.text_input("Location", value="Earlwood, NSW")

    if st.button("Generate meal", type="primary"):
        with st.spinner("Planning meal..."):
            meal_result = post_json(
                "/generate-meal-plan",
                {
                    "user_id": user_id,
                    "craving": craving,
                    "location": location,
                },
            )
        st.json(meal_result)

with calorie_col:
    st.subheader("Predict Calories")
    if st.button("Predict expenditure"):
        conditions = [item.strip() for item in health_conditions.split(",") if item.strip()]
        with st.spinner("Predicting calorie budget..."):
            calorie_result = post_json(
                "/calorie-expenditure/predict",
                {
                    "age": age,
                    "sex": sex,
                    "height_cm": height_cm,
                    "weight_kg": weight_kg,
                    "activity_multiplier": activity_multiplier,
                    "goal": goal,
                    "health_conditions": conditions,
                },
            )
        st.metric(
            "Meal calorie budget",
            f"{calorie_result['meal_calorie_budget_kcal']:,.0f} kcal",
        )
        st.json(calorie_result)
