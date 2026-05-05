import os
from dataclasses import dataclass
from pathlib import Path
from typing import List

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
if os.getenv("SKIP_DOTENV") != "1":
    load_dotenv(BASE_DIR / "backend" / ".env")


def _csv_env(name: str, default: str) -> List[str]:
    raw_value = os.getenv(name, default)
    return [value.strip() for value in raw_value.split(",") if value.strip()]


@dataclass(frozen=True)
class AppSettings:
    app_name: str
    environment: str
    allowed_origins: List[str]
    gemini_api_key: str | None
    usda_api_key: str | None
    fatsecret_client_id: str | None
    fatsecret_client_secret: str | None
    maps_api_key: str | None
    inventory_api_key: str | None
    data_dir: Path

    @classmethod
    def from_env(cls) -> "AppSettings":
        return cls(
            app_name=os.getenv("APP_NAME", "Multi-Agent Meal Planner API"),
            environment=os.getenv("APP_ENV", "development"),
            allowed_origins=_csv_env(
                "ALLOWED_ORIGINS",
                "http://localhost:5173,http://127.0.0.1:5173",
            ),
            gemini_api_key=os.getenv("GEMINI_API_KEY"),
            usda_api_key=os.getenv("USDA_API_KEY"),
            fatsecret_client_id=os.getenv("FATSECRET_CLIENT_ID"),
            fatsecret_client_secret=os.getenv("FATSECRET_CLIENT_SECRET"),
            maps_api_key=os.getenv("MAPS_API_KEY"),
            inventory_api_key=os.getenv("INVENTORY_API_KEY"),
            data_dir=BASE_DIR / "database",
        )
