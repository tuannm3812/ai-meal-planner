"""The History tab: load meal history and saved meals."""

from collections.abc import Callable
from typing import Any

import streamlit as st
from api import render_api_error
from config import AppConfig


def render(config: AppConfig, call_api: Callable[..., dict[str, Any]]) -> None:
    """Render the History tab.

    Args:
        config: The sidebar's resolved configuration.
        call_api: Request function bound to the config, demo or live.
    """
    st.subheader("Meal History")
    history_limit = st.slider("Limit", 1, 50, 10)
    if st.button("Load history"):
        try:
            with st.spinner("Loading meal history..."):
                history_result = call_api(
                    "GET",
                    f"/meal-plans/{config.user_id}?limit={history_limit}",
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
                saved_result = call_api(
                    "GET",
                    f"/saved-meals/{config.user_id}?limit={history_limit}",
                )
            items = saved_result.get("items", [])
            st.metric("Saved", len(items))
            if items:
                st.json(saved_result)
            else:
                st.info("No saved meals yet — mark a meal as saved from the Meal Plan tab.")
        except Exception as exc:
            render_api_error(exc)
