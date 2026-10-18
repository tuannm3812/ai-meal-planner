"""The Meal Plan tab: request a meal, show the result, collect feedback."""

from collections.abc import Callable
from typing import Any

import streamlit as st
from api import render_api_error
from config import AppConfig


def is_meal_like_input(value: str) -> bool:
    """Reject input that is not a meal request before it reaches the API.

    Args:
        value: The raw craving or meal goal typed by the user.

    Returns:
        False for polite-only input such as "thanks" or "ok", or anything under
        three characters once trimmed; True otherwise.
    """
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


def render(config: AppConfig, call_api: Callable[..., dict[str, Any]]) -> None:
    """Render the Meal Plan tab.

    Args:
        config: The sidebar's resolved configuration.
        call_api: Request function bound to the config, demo or live.
    """
    if "latest_meal_result" not in st.session_state:
        st.session_state.latest_meal_result = None

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
                        meal_result = call_api(
                            "POST",
                            "/generate-meal-plan",
                            {
                                "user_id": config.user_id,
                                "craving": craving,
                                "location": location,
                                "health_conditions": config.health_conditions,
                                "dietary_preferences": config.dietary_preferences,
                            },
                        )

                    if meal_result.get("plan_status") == "infeasible":
                        # No meal to show or give feedback on: say why instead.
                        st.session_state.latest_meal_result = None
                        st.warning(meal_result.get("infeasible_reason") or "No meal fits.")
                    else:
                        st.session_state.latest_meal_result = meal_result
                        _render_meal_result(meal_result, craving)
                except Exception as exc:
                    render_api_error(exc)
        else:
            st.info("Submit a craving to call `/generate-meal-plan`.")

        latest_meal_result = st.session_state.latest_meal_result
        # G6: a hosted API refuses feedback, so the form is hidden there.
        if latest_meal_result and not config.hosted_mode:
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
                    feedback_result = call_api(
                        "POST",
                        "/meal-feedback",
                        {
                            "user_id": config.user_id,
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


# The service decides whether a plan meets the targets (DEC-25, DEC-26); the
# demo only reports its macro_balance record, as the React dashboard does.
BALANCE_OUTCOMES = {
    "in_range": (
        "On target",
        "Calories and the protein, carb and fat split are inside the recommended ranges.",
    ),
    "rebalanced": (
        "Portions rebalanced",
        "Ingredient portions were resized so the meal fits the recommended ranges.",
    ),
    "no_feasible_balance": (
        "Outside the ranges",
        "This meal's ingredients cannot be resized into the recommended ranges.",
    ),
    "reverted": (
        "Outside the ranges",
        "Resized portions missed the ranges once checked, so the original portions are shown.",
    ),
}


def _render_meal_quality(meal_result: dict[str, Any], craving: str) -> None:
    """Say whether the plan is a close match and whether it meets the targets.

    Args:
        meal_result: The /generate-meal-plan response for a plan with a meal.
        craving: What the user asked for.
    """
    if meal_result.get("plan_status") == "fallback":
        st.warning(
            f"Nothing on the menu is a close match for \u201c{craving}\u201d, "
            "so this is a standard meal instead."
        )
    balance = meal_result.get("macro_balance")
    if not balance or balance.get("outcome") not in BALANCE_OUTCOMES:
        return
    label, body = BALANCE_OUTCOMES[balance["outcome"]]
    split = (
        balance.get("macro_percent_after")
        if balance["outcome"] == "rebalanced"
        else balance.get("macro_percent_before")
    ) or {}
    st.markdown(f"**Meal quality: {label}.** {body}")
    split_cols = st.columns(4)
    for col, (key, name) in zip(
        split_cols, (("protein", "Protein"), ("carbs", "Carbs"), ("fat", "Fat")), strict=False
    ):
        col.metric(f"{name} share", f"{round(split.get(key, 0))}%")
    split_cols[3].metric("Meal target", f"{balance.get('target_meal_calories', 0)} kcal")


def _render_meal_result(meal_result: dict[str, Any], craving: str = "") -> None:
    """Render a matched or fallback meal plan.

    Args:
        meal_result: The /generate-meal-plan response for a plan with a meal.
        craving: What the user asked for, named in the no-match notice.
    """
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
    _render_meal_quality(meal_result, craving)

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
