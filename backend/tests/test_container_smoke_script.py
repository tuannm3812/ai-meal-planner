"""The container smoke script must be isolated from the developer's own stack.

Codex, 2026-10-10 (two P2s on PR #14):

1. The script used compose.yaml's fixed project name and published ports, so
   against a developer's running stack it reused that stack, and its EXIT trap
   removed those containers, and their unpersisted history, even when startup
   failed.
2. It inherited the operator's shell and root .env (API_KEYS, provider keys,
   REQUIRE_VERIFIED_NUTRITION), so its "anonymous, offline" checks were neither.

These tests run the real script against a fake `docker` that records every call
and the environment it saw, then fails `compose up`. They need no Docker
daemon, and they cannot touch real containers.
"""

import os
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = ["container_smoke.sh", "hosted_smoke.sh"]
OPERATOR_KEYS = '[{"client_id": "real"}]'
WATCHED = (
    "API_KEYS",
    "GEMINI_API_KEY",
    "USDA_API_KEY",
    "FATSECRET_CLIENT_ID",
    "FATSECRET_CLIENT_SECRET",
    "REQUIRE_VERIFIED_NUTRITION",
    "MEAL_PLANNER_API_KEY",
    "APP_ENV",
)

FAKE_DOCKER = """#!/usr/bin/env bash
log="$FAKE_DOCKER_LOG"
printf 'ARGS %s\\n' "$*" >> "$log"
for name in {watched}; do
  printf 'ENV %s=%s\\n' "$name" "${{!name-<unset>}}" >> "$log"
done
case " $* " in
  *" up "*) exit 1 ;;
esac
exit 0
"""


@pytest.fixture(name="run", params=SCRIPTS)
def _run(
    request: pytest.FixtureRequest, tmp_path: Path
) -> tuple[subprocess.CompletedProcess[str], list[str]]:
    """Run each smoke script with a hostile operator environment and a failing `up`."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake = bin_dir / "docker"
    fake.write_text(FAKE_DOCKER.format(watched=" ".join(WATCHED)))
    fake.chmod(0o755)
    log = tmp_path / "docker.log"

    env = {
        **os.environ,
        "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
        "FAKE_DOCKER_LOG": str(log),
        # A developer's own configuration, which the smoke run must not inherit.
        "COMPOSE_PROJECT_NAME": "ai-meal-planner",
        "API_KEYS": OPERATOR_KEYS,
        "GEMINI_API_KEY": "real-gemini-key",
        "USDA_API_KEY": "real-usda-key",
        "FATSECRET_CLIENT_ID": "real-id",
        "FATSECRET_CLIENT_SECRET": "real-secret",
        "REQUIRE_VERIFIED_NUTRITION": "1",
        "MEAL_PLANNER_API_KEY": "real-streamlit-key",
        "APP_ENV": "production",
    }
    script = REPO / "scripts" / request.param
    result = subprocess.run(
        ["bash", str(script)], env=env, cwd=REPO, capture_output=True, text=True, timeout=60
    )
    lines = log.read_text().splitlines() if log.exists() else []
    return result, [f"SCRIPT {request.param}", *lines]


def _compose_calls(lines: list[str]) -> list[str]:
    return [line[5:] for line in lines if line.startswith("ARGS compose ")]


def _project(call: str) -> str:
    parts = call.split()
    return parts[parts.index("--project-name") + 1]


def test_a_failed_startup_exits_non_zero(
    run: tuple[subprocess.CompletedProcess[str], list[str]],
) -> None:
    result, _ = run

    assert result.returncode != 0


def test_every_compose_call_uses_a_run_specific_project(
    run: tuple[subprocess.CompletedProcess[str], list[str]],
) -> None:
    """Never the developer's `ai-meal-planner` project, before or during cleanup."""
    _, lines = run
    calls = _compose_calls(lines)

    assert any(" up " in f" {c} " for c in calls), calls
    assert any(" down " in f" {c} " for c in calls), "cleanup must still run"
    projects = {_project(call) for call in calls}
    assert len(projects) == 1, projects
    (project,) = projects
    assert project != "ai-meal-planner"
    assert project.startswith("ai-meal-planner-smoke-")


def test_the_run_uses_its_own_image_and_removes_only_that(
    run: tuple[subprocess.CompletedProcess[str], list[str]],
) -> None:
    _, lines = run
    removed = [line for line in lines if line.startswith("ARGS image rm")]

    assert removed, "the run-specific image must be cleaned up"
    for line in removed:
        assert "ai-meal-planner:local" not in line
        assert "ai-meal-planner:smoke-" in line


def test_the_operators_dotenv_is_bypassed(
    run: tuple[subprocess.CompletedProcess[str], list[str]],
) -> None:
    _, lines = run

    for call in _compose_calls(lines):
        parts = call.split()
        assert "--env-file" in parts, call
        env_file = parts[parts.index("--env-file") + 1]
        assert Path(env_file).name != ".env"


def test_the_operators_keys_and_strictness_never_reach_compose(
    run: tuple[subprocess.CompletedProcess[str], list[str]],
) -> None:
    """What compose interpolates from: smoke-only values, not the operator's."""
    _, lines = run
    script = lines[0].removeprefix("SCRIPT ")
    seen: dict[str, set[str]] = {}
    for line in lines:
        if line.startswith("ENV "):
            name, _, value = line[4:].partition("=")
            seen.setdefault(name, set()).add(value)

    for name in (
        "GEMINI_API_KEY",
        "USDA_API_KEY",
        "FATSECRET_CLIENT_ID",
        "FATSECRET_CLIENT_SECRET",
        "MEAL_PLANNER_API_KEY",
    ):
        assert seen[name] == {""}, (script, name, seen[name])
    assert seen["REQUIRE_VERIFIED_NUTRITION"] == {"0"}, script
    if script == "container_smoke.sh":
        # Open, keyless local mode.
        assert seen["API_KEYS"] == {""}
        assert seen["APP_ENV"] == {"development"}
    else:
        # A throwaway key generated per run - never the operator's key list. (The
        # hosted compose file pins APP_ENV=production itself.)
        (keys,) = seen["API_KEYS"]
        assert keys not in {"", OPERATOR_KEYS}
        assert '"client_id": "smoke"' in keys
