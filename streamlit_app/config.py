"""Secret and configuration lookup for the Streamlit app."""

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import streamlit as st
from pydantic import TypeAdapter


def get_secret(name: str, default: str = "") -> str:
    env_value = os.getenv(name)
    if env_value:
        return env_value

    try:
        value = st.secrets.get(name)
        if value:
            return str(value)
    except Exception:
        pass

    local_secrets_path = Path(".streamlit") / "secrets.toml"
    if local_secrets_path.exists():
        try:
            secrets = tomllib.loads(local_secrets_path.read_text(encoding="utf-8"))
            value = secrets.get(name)
            if value:
                return str(value)
        except tomllib.TOMLDecodeError:
            return default

    return default


def get_bool_secret(name: str, default: bool = False) -> bool:
    """Read a boolean setting exactly as the API's pydantic settings do.

    Demo mode used to compare these flags to "1". The API parses a pydantic
    boolean, so "true", "yes", "on", and a native TOML `true` (stringified to
    "True" by get_secret) enabled a setting in the API but not in the demo.
    Reusing pydantic's parser keeps the two modes identical, including refusing
    an unparseable value, which the API also refuses at startup.

    Args:
        name: The environment variable or secrets key.
        default: The value when the setting is absent or empty.

    Returns:
        The parsed boolean.

    Raises:
        pydantic.ValidationError: If the value is not a recognised boolean.
    """
    raw = get_secret(name)
    if not raw:
        return default
    return TypeAdapter(bool).validate_python(raw)


@dataclass(frozen=True)
class AppConfig:
    """Everything the sidebar resolves that the tabs need.

    The tabs previously read these as module globals, which no view module can
    do. The sidebar returns this instead and app.py threads it through.

    The body metrics appear both as fields and inside ``profile``: the calorie tab
    sends them as its own request payload, while ``profile`` is the demo-mode user
    profile built from the same widgets.
    """

    use_demo_mode: bool
    api_base_url: str
    gemini_api_key: str
    user_id: str
    profile: dict[str, Any]
    health_conditions: list[str]
    dietary_preferences: list[str]
    age: int
    sex: str
    height_cm: float
    weight_kg: float
    activity_multiplier: float
    duration_minutes: float
    heart_rate_bpm: float
    body_temp_c: float
    goal: str
    # G6: true when the API's /health reports a hosted, stateless deployment,
    # where history and feedback are refused. Demo mode is never hosted.
    hosted_mode: bool = False
