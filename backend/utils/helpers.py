"""
Shared helpers: JSON serialization, env loading, and input sanitization.
"""

import json
import os
from typing import Any, Optional

from dotenv import load_dotenv

# Load .env from backend/ on import
load_dotenv()


def get_env(key: str, default: Optional[str] = None) -> Optional[str]:
    """Read an environment variable with an optional default."""
    return os.getenv(key, default)


def require_env(key: str) -> str:
    """Read a required environment variable or raise a clear error."""
    value = os.getenv(key)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {key}")
    return value


def to_json(data: Any) -> str:
    """Serialize Python objects to a JSON string."""
    return json.dumps(data, ensure_ascii=False, default=str)


def from_json(raw: Optional[str], fallback: Any = None) -> Any:
    """Deserialize a JSON string; return fallback on empty/invalid input."""
    if not raw:
        return fallback
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return fallback


def interests_to_str(interests: list[str]) -> str:
    """Join interest list into a stored string."""
    return ",".join(i.strip().lower() for i in interests if i and i.strip())


def interests_from_str(raw: Optional[str]) -> list[str]:
    """Split stored interests string back into a list."""
    if not raw:
        return []
    return [part.strip() for part in raw.split(",") if part.strip()]


def build_trip_title(destination: str, number_of_days: int) -> str:
    """Generate a readable default trip title."""
    return f"{number_of_days}-Day Trip to {destination.strip().title()}"
