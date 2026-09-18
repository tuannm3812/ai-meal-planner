"""Secret and configuration lookup for the Streamlit app."""

import os
import tomllib
from pathlib import Path

import streamlit as st


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
