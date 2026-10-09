"""HTTP helpers for talking to the FastAPI backend from the Streamlit app."""

from typing import Any

import requests
import streamlit as st


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

    # Demo mode runs the backend in-process, so its domain exceptions arrive here
    # directly. Show their client-safe message: str(exc) is the internal detail,
    # which can name the user's health constraints.
    client_message = getattr(exc, "client_message", None)
    if client_message:
        st.error(client_message)
        return

    st.error(f"Unexpected API error: {exc}")


def parse_extra_items(raw_value: str) -> list[str]:
    return [item.strip() for item in raw_value.split(",") if item.strip()]
