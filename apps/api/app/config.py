from dataclasses import dataclass
from pathlib import Path
import os
from typing import Tuple


def _resolve_database_path(raw_path: str) -> str:
    candidate = Path(raw_path)
    if candidate.is_absolute():
        return str(candidate)
    return str((Path.cwd() / candidate).resolve())


def _parse_allowed_origins(raw_value: str) -> Tuple[str, ...]:
    items = tuple(origin.strip() for origin in raw_value.split(",") if origin.strip())
    if not items:
        return ("*",)
    return items


@dataclass(frozen=True)
class Settings:
    worldengine_api_base: str
    database_path: str
    allowed_origins: Tuple[str, ...]


def get_settings() -> Settings:
    worldengine_api_base = os.getenv("WORLDENGINE_API_BASE", "http://127.0.0.1:8000").rstrip("/")
    database_path = _resolve_database_path(
        os.getenv("WORLDENGINE_VALIDATION_DATABASE_PATH", ".worldengine-validation-client/client.sqlite3")
    )
    allowed_origins = _parse_allowed_origins(
        os.getenv("WORLDENGINE_VALIDATION_ALLOWED_ORIGINS", "*")
    )
    return Settings(
        worldengine_api_base=worldengine_api_base,
        database_path=database_path,
        allowed_origins=allowed_origins,
    )
