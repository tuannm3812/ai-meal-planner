"""The Calories tab: predict calorie expenditure from the sidebar profile."""

from collections.abc import Callable
from typing import Any

import streamlit as st
from api import render_api_error
from config import AppConfig


def render(config: AppConfig, call_api: Callable[..., dict[str, Any]]) -> None:
    """Render the Calories tab.

    Args:
        config: The sidebar's resolved configuration.
        call_api: Request function bound to the config, demo or live.
    """
    st.subheader("Calorie Expenditure")
    calorie_payload = {
        "age": config.age,
        "sex": config.sex,
        "height_cm": config.height_cm,
        "weight_kg": config.weight_kg,
        "activity_multiplier": config.activity_multiplier,
        "duration_minutes": config.duration_minutes,
        "heart_rate_bpm": config.heart_rate_bpm,
        "body_temp_c": config.body_temp_c,
        "goal": config.goal,
        "health_conditions": config.health_conditions,
    }

    st.caption(
        "This calls `/calorie-expenditure/predict` using the promoted Kaggle model artifact."
    )
    if config.health_conditions:
        st.warning(
            "Health conditions are passed as constraints only. This app does "
            "not provide medical advice."
        )
    if config.dietary_preferences:
        st.info(
            "Dietary preferences selected for upcoming recommendation work: "
            f"{', '.join(config.dietary_preferences)}"
        )
    with st.expander("Request payload"):
        st.json(calorie_payload)

    if st.button("Predict expenditure", type="primary"):
        try:
            with st.spinner("Predicting calorie budget..."):
                calorie_result = call_api(
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
