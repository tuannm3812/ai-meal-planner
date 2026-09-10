"""Application settings, resolved from the environment."""

import os
from pathlib import Path
from typing import Annotated, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[3]


def _resolve_repo_path(path_value: Path | str) -> Path:
    """Resolve a possibly-relative path against the repository root.

    Args:
        path_value: An absolute path, or one relative to the repo root.

    Returns:
        An absolute path. Resolving against the repo root rather than the
        process's working directory means the API behaves the same however it
        is started.
    """
    path = Path(path_value)
    return path if path.is_absolute() else BASE_DIR / path


class AppSettings(BaseSettings):
    """Every setting the application reads, with its default."""

    model_config = SettingsConfigDict(
        env_file=None if os.getenv("SKIP_DOTENV") == "1" else BASE_DIR / "backend" / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "Multi-Agent Meal Planner API"
    environment: str = Field(default="development", alias="APP_ENV")
    allowed_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://127.0.0.1:5173"]
    )

    gemini_api_key: str | None = None
    usda_api_key: str | None = None
    fatsecret_client_id: str | None = None
    fatsecret_client_secret: str | None = None
    maps_api_key: str | None = None
    inventory_api_key: str | None = None

    calorie_model_path: Path = (
        BASE_DIR / "models" / "calorie_expenditure" / "calorie_expenditure_model.joblib"
    )
    calorie_model_version: str = "hist_gradient_boosting_deep_v0.1.0"
    meal_corpus_path: Path = BASE_DIR / "data" / "meal_corpus" / "meals.json"
    rag_backend: str = "auto"
    rag_embedding_cache_dir: Path = BASE_DIR / "data" / "vector_index"
    rag_embedding_activation_size: int = 50
    enable_gemini_adaptation: bool = False

    storage_backend: Literal["json", "sqlite"] = "sqlite"

    @property
    def data_dir(self) -> Path:
        """Directory holding the JSON stores and the SQLite database."""
        return BASE_DIR / "database"

    @property
    def sqlite_path(self) -> Path:
        """Filesystem location of the SQLite database."""
        return self.data_dir / "ai_meal_planner.db"

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def _split_csv(cls, value: object) -> object:
        """Accept ALLOWED_ORIGINS as a comma-separated string.

        Args:
            value: The raw environment value, or an already-parsed list.

        Returns:
            A list of origins with blanks removed, or the value unchanged when
            it is not a string.
        """
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @field_validator("calorie_model_path", "meal_corpus_path", "rag_embedding_cache_dir")
    @classmethod
    def _resolve(cls, value: Path) -> Path:
        """Resolve configured paths against the repository root.

        Args:
            value: The configured path, absolute or repo-relative.

        Returns:
            An absolute path.
        """
        return _resolve_repo_path(value)

    @classmethod
    def from_env(cls) -> "AppSettings":
        """Build settings from the environment.

        Retained so existing call sites keep working after the migration to
        pydantic-settings.

        Returns:
            A populated AppSettings.
        """
        return cls()
