"""Settings must resolve from the environment with correct defaults."""

from pathlib import Path

import pytest

from backend.app.core.config import AppSettings


def test_defaults_are_unchanged() -> None:
    """The values the app relied on before pydantic-settings still hold.

    ``_env_file=None`` keeps a developer's real backend/.env from being read
    here: AppSettings() would otherwise assert whatever that file happens to
    contain rather than the library's actual defaults.
    """
    settings = AppSettings(_env_file=None)
    assert settings.app_name == "Multi-Agent Meal Planner API"
    assert settings.environment == "development"
    assert settings.rag_backend == "auto"
    assert settings.rag_embedding_activation_size == 50
    assert settings.enable_gemini_adaptation is False


def test_storage_backend_defaults_to_sqlite() -> None:
    """``_env_file=None`` isolates the default from a developer's backend/.env."""
    assert AppSettings(_env_file=None).storage_backend == "sqlite"


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
    """``_env_file=None`` isolates the default from a developer's backend/.env."""
    settings = AppSettings(_env_file=None)
    assert settings.sqlite_path == settings.data_dir / "ai_meal_planner.db"
    assert isinstance(settings.sqlite_path, Path)


def test_environment_is_settable_by_field_name_and_by_alias(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Both forms must work, and neither may silently fall back to the default.

    `environment` is aliased to APP_ENV. Without populate_by_name, constructing
    AppSettings(environment=...) silently yielded "development" because
    extra="ignore" swallowed the keyword.
    """
    monkeypatch.setenv("APP_ENV", "staging")
    assert AppSettings().environment == "staging"
    monkeypatch.delenv("APP_ENV", raising=False)
    assert AppSettings(environment="by-field-name").environment == "by-field-name"
    assert AppSettings(APP_ENV="by-alias").environment == "by-alias"
