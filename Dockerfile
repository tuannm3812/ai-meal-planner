# syntax=docker/dockerfile:1
#
# G5b: one image for the FastAPI backend, which compose also runs as the
# Streamlit client. Dependencies come from uv.lock, the single source behind the
# generated requirements files (DEC-6), so the image and CI resolve the same
# versions. History is stored inside the container and is not persisted: that
# is stateless v1, by design. No migration or data import runs at build time.

ARG PYTHON_IMAGE=python:3.11-slim-bookworm

FROM ghcr.io/astral-sh/uv:0.11.29 AS uv

# ---- builder: resolve the locked runtime dependencies into /app/.venv --------
FROM ${PYTHON_IMAGE} AS builder
COPY --from=uv /uv /bin/uv
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never
WORKDIR /app
COPY pyproject.toml uv.lock ./
# --no-dev: no test tooling in the image. --no-install-project: the code is
# copied in below and imported from /app, so there is no wheel to build.
# --extra tracing: the OpenTelemetry SDK and exporter, idle unless
# TRACING_EXPORTER is set (G10b).
RUN uv sync --locked --no-dev --no-install-project --extra tracing

# ---- runtime: the venv, the code and the shipped assets, as a non-root user --
FROM ${PYTHON_IMAGE} AS runtime
RUN groupadd --system app && useradd --system --gid app --home-dir /app app
WORKDIR /app
COPY --from=builder --chown=app:app /app/.venv /app/.venv
COPY --chown=app:app backend/__init__.py backend/__init__.py
COPY --chown=app:app backend/app backend/app
COPY --chown=app:app streamlit_app streamlit_app
COPY --chown=app:app models/calorie_expenditure models/calorie_expenditure
COPY --chown=app:app data/meal_corpus data/meal_corpus
COPY --chown=app:app data/reference data/reference
# Writable, empty storage. A *new* container starts with empty history;
# restarting the same container keeps its writable layer, so history survives a
# restart but not a recreate or redeploy (Codex, 2026-10-10). /app
# and data/ were created by root above; the non-root user needs them writable
# (Streamlit writes under HOME=/app, and caches may be created under data/).
RUN mkdir -p database && chown app:app /app /app/data database

ENV PATH="/app/.venv/bin:${PATH}" \
    PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HOME=/app
USER app
EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=3s --start-period=20s --retries=5 \
    CMD ["python", "-c", "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3).status == 200 else 1)"]

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
