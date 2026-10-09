import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import streamlit as st
from api import request_json, with_api_key
from config import AppConfig
from demo import local_demo_request
from views import calories, history, meal_plan
from views.sidebar import render_sidebar

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

st.set_page_config(page_title="AI Meal Planner", page_icon="A", layout="wide")

st.title("AI Meal Planner")

config = render_sidebar()


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
        return request_json(
            method,
            config.api_base_url,
            path,
            payload,
            with_api_key(config.api_base_url, headers),
        )

    return call_demo_or_api


call_api = make_request(config)

meal_tab, calorie_tab, history_tab = st.tabs(["Meal Plan", "Calories", "History"])

with meal_tab:
    meal_plan.render(config, call_api)
with calorie_tab:
    calories.render(config, call_api)
with history_tab:
    history.render(config, call_api)
