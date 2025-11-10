import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


class Config:
    def __init__(self, env_path: Path | None = None):
        self._root_path = Path(__file__).parent.parent
        load_dotenv(env_path or self._root_path / ".env")

    def __getattr__(self, name: str) -> Any:
        value = os.getenv(name)
        if value is None:
            return None
        return self._convert_value(value)

    @staticmethod
    def _convert_value(value: str) -> Any:
        if value.lower() in ("true", "false"):
            return value.lower() == "true"
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return value
