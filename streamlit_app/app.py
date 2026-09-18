import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import streamlit as st
from api import render_api_error, request_json
from config import AppConfig
from demo import local_demo_request
from views.sidebar import render_sidebar

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

st.set_page_config(page_title="AI Meal Planner", page_icon="A", layout="wide")


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

config = render_sidebar()
use_demo_mode = config.use_demo_mode
api_base_url = config.api_base_url
gemini_api_key = config.gemini_api_key
user_id = config.user_id
streamlit_profile = config.profile
selected_health_conditions = config.health_conditions
dietary_preferences = config.dietary_preferences
age = config.age
sex = config.sex
height_cm = config.height_cm
weight_kg = config.weight_kg
activity_multiplier = config.activity_multiplier
duration_minutes = config.duration_minutes
heart_rate_bpm = config.heart_rate_bpm
body_temp_c = config.body_temp_c
goal = config.goal


def make_request(config: AppConfig) -> Callable[..., dict[str, Any]]:
    """Build the request function the views use, bound to the current config.

    Args:
        config: The sidebar's resolved configuration.

    Returns:
        A callable with the same signature the tabs already use.
    """

    def call_demo_or_api(
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        if config.use_demo_mode:
            return local_demo_request(
                path=path,
                payload=payload,
                profile=config.profile,
                api_key=config.gemini_api_key,
            )
        return request_json(method, config.api_base_url, path, payload, headers)

    return call_demo_or_api


call_demo_or_api = make_request(config)


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
