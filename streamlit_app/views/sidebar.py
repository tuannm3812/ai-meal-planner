"""The sidebar: run mode, API health, optional keys, then the Profile section."""

from typing import Any

import streamlit as st
from api import render_api_error, request_json
from config import AppConfig, get_secret
from demo import local_demo_request

from views.profile import render_profile


def render_sidebar() -> AppConfig:
    """Render the sidebar controls and resolve them into the app's configuration.

    The health check calls ``local_demo_request`` and ``request_json`` directly
    rather than through the tabs' request callable, because that callable is built
    from the config this function is still assembling.

    Returns:
        Every sidebar value the tabs consume, plus the derived health conditions
        and demo-mode profile.
    """
    # Resolved per call, not at import: app.py re-read it on every script rerun.
    default_api_base_url = get_secret("API_BASE_URL", "http://localhost:8000")

    with st.sidebar:
        st.subheader("Run Mode")
        use_demo_mode = st.toggle(
            "Self-contained Streamlit demo",
            value=get_secret("STREAMLIT_DEMO_MODE", "0") == "1",
            help="Run the demo directly inside Streamlit without calling FastAPI.",
        )
        api_base_url = default_api_base_url
        if use_demo_mode:
            st.caption(
                "Using local agents inside Streamlit. FastAPI is not required for this demo."
            )
        else:
            st.subheader("API")
            api_base_url = st.text_input("Base URL", value=default_api_base_url)
        health_payload: dict[str, Any] = {}
        with st.expander("Deployment settings"):
            st.markdown(
                "\n".join(
                    [
                        "**Streamlit Cloud**",
                        "- Repository: `tuannm3812/ai-meal-planner`",
                        "- Branch: `main`",
                        "- Main file path: `streamlit_app/app.py`",
                        "- App URL: choose an available slug such as `tuannm-ai-meal-planner`",
                        "",
                        "**Secrets**",
                        "```toml",
                        'API_BASE_URL = "https://your-backend-url"',
                        'STREAMLIT_DEMO_MODE = "1"',
                        'GEMINI_API_KEY = "optional-key-for-final-explanations"',
                        "```",
                    ]
                )
            )

        try:
            if use_demo_mode:
                health_payload = local_demo_request(
                    "/health",
                    None,
                    {
                        "age": 28,
                        "sex": "male",
                        "height_cm": 180.0,
                        "weight_kg": 80.0,
                        "activity_multiplier": 1.55,
                        "dietary_restrictions": ["dairy-free", "high-protein"],
                    },
                    get_secret("GEMINI_API_KEY"),
                )
                st.success("Demo mode ready")
            else:
                health_payload = request_json("GET", api_base_url, "/health")
                st.success("API online")
            services = health_payload.get("services", {})
            status_lines = [
                ("Gemini", services.get("gemini_configured")),
                ("USDA", services.get("usda_configured")),
                ("FatSecret", services.get("fatsecret_configured")),
                ("Calorie model", services.get("calorie_model_configured")),
            ]
            for label, configured in status_lines:
                if configured:
                    st.success(f"{label}: configured", icon="✅")
                else:
                    st.warning(f"{label}: not configured", icon="⚠️")
            rag_backend = services.get("rag_backend")
            if rag_backend:
                st.caption(f"RAG backend: `{rag_backend}`")
            with st.expander("Full health payload"):
                st.json(health_payload)
        except Exception as exc:
            st.warning("API offline, unreachable, or demo mode unavailable")
            with st.expander("Connection details"):
                render_api_error(exc)

        gemini_api_key = get_secret("GEMINI_API_KEY")
        with st.expander("Optional AI keys"):
            gemini_key_source = (
                "configured"
                if health_payload.get("services", {}).get("gemini_configured") or gemini_api_key
                else "not configured"
            )
            st.caption(f"Gemini status: {gemini_key_source}")
            gemini_api_key = st.text_input(
                "Gemini API key",
                value=gemini_api_key,
                type="password",
                help=(
                    "Optional, demo mode only. Gemini is only used for the final "
                    "explanation when enabled. In API mode the server uses its own key."
                ),
            )

        st.divider()
        profile_fields = render_profile()

    return AppConfig(
        use_demo_mode=use_demo_mode,
        api_base_url=api_base_url,
        gemini_api_key=gemini_api_key,
        hosted_mode=bool(health_payload.get("services", {}).get("hosted_mode")),
        **profile_fields,
    )
