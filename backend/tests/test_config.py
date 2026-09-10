"""Settings must resolve from the environment with correct defaults."""

from pathlib import Path

import pytest

from backend.app.core.config import AppSettings


def test_defaults_are_unchanged() -> None:
    """The values the app relied on before pydantic-settings still hold."""
    settings = AppSettings()
    assert settings.app_name == "Multi-Agent Meal Planner API"
    assert settings.environment == "development"
    assert settings.rag_backend == "auto"
    assert settings.rag_embedding_activation_size == 50
    assert settings.enable_gemini_adaptation is False


def test_storage_backend_defaults_to_sqlite() -> None:
    assert AppSettings().storage_backend == "sqlite"


@pytest.mark.parametrize("value", ["json", "sqlite"])
def test_storage_backend_accepts_both_values(monkeypatch: pytest.MonkeyPatch, value: str) -> None:
    monkeypatch.setenv("STORAGE_BACKEND", value)
    assert AppSettings().storage_backend == value


def test_storage_backend_rejects_anything_else(monkeypatch: pytest.MonkeyPatch) -> None:
    """A typo must fail loudly at startup, not silently pick a backend."""
    monkeypatch.setenv("STORAGE_BACKEND", "postgres")
    with pytest.raises(ValueError):
        AppSettings()


def test_allowed_origins_parses_a_comma_separated_list(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ALLOWED_ORIGINS", "http://a.test, http://b.test")
    assert AppSettings().allowed_origins == ["http://a.test", "http://b.test"]


def test_relative_paths_resolve_against_the_repo_root(monkeypatch: pytest.MonkeyPatch) -> None:
    """A relative MEAL_CORPUS_PATH must not depend on the process's cwd."""
    monkeypatch.setenv("MEAL_CORPUS_PATH", "data/meal_corpus/meals.json")
    resolved = AppSettings().meal_corpus_path
    assert resolved.is_absolute()
    assert resolved.exists()


def test_from_env_still_works() -> None:
    """Existing call sites use AppSettings.from_env(); it must keep working."""
    assert isinstance(AppSettings.from_env(), AppSettings)


def test_sqlite_path_defaults_under_the_data_dir() -> None:
    settings = AppSettings()
    assert settings.sqlite_path == settings.data_dir / "ai_meal_planner.db"
    assert isinstance(settings.sqlite_path, Path)
