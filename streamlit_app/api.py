"""HTTP helpers for talking to the FastAPI backend from the Streamlit app."""

from typing import Any
from urllib.parse import urlsplit

import requests
import streamlit as st
from config import get_secret


def request_json(
    method: str,
    base_url: str,
    path: str,
    payload: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> dict[str, Any]:
    url = f"{base_url.rstrip('/')}{path}"
    # Never follow redirects. requests strips only Authorization on a cross-host
    # redirect, so an X-API-Key header would follow a 30x to another host. The
    # API has no redirect routes, so any 3xx is treated as an error.
    response = requests.request(
        method, url, json=payload, headers=headers, timeout=30, allow_redirects=False
    )
    if response.is_redirect:
        raise requests.HTTPError(
            f"Refused to follow a {response.status_code} redirect from {url}.",
            response=response,
        )
    response.raise_for_status()
    return response.json()


_DEFAULT_PORTS = {"http": 80, "https": 443}


def _origin(url: str) -> tuple[str, str, int] | None:
    """Return (scheme, host, port) for an http(s) URL, or None if it cannot be trusted.

    A URL carrying userinfo is never trusted: "http://localhost:8000@evil" is a
    request to "evil", and even credentials for the right host are not ours to
    accept from a visitor.
    """
    try:
        parts = urlsplit(url.strip())
        port = parts.port
    except ValueError:
        return None
    scheme = parts.scheme.lower()
    if scheme not in _DEFAULT_PORTS or not parts.hostname or "@" in parts.netloc:
        return None
    return scheme, parts.hostname.lower(), port or _DEFAULT_PORTS[scheme]


def with_api_key(base_url: str, headers: dict[str, str] | None) -> dict[str, str] | None:
    """Add the server-side API key, but only for the operator's own backend.

    G4: a keyed API needs X-API-Key, read from the MEAL_PLANNER_API_KEY secret
    and never shown in the UI. A visitor can edit the sidebar's Base URL, so
    the key is bound to the operator-controlled API_BASE_URL secret: it is
    attached only when ``base_url`` has the same scheme, host and port (Codex
    P1, 2026-10-10). Any other URL still works, unauthenticated, which suits an
    API in open local mode during development.

    Args:
        base_url: Where this request is going.
        headers: Headers the caller already set, if any.

    Returns:
        The headers, with X-API-Key added only for the configured backend.
    """
    key = get_secret("MEAL_PLANNER_API_KEY")
    trusted = _origin(get_secret("API_BASE_URL", "http://localhost:8000"))
    if not key or trusted is None or _origin(base_url) != trusted:
        return headers
    return {**(headers or {}), "X-API-Key": key}


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
