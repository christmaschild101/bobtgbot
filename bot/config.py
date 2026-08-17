"""Configuration helpers for Bob."""

from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"


def load_env_file() -> None:
    """Load key=value lines from a local .env file (no external dependency)."""
    if not ENV_FILE.exists():
        return
    for raw in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def get_token() -> str:
    """Return the bot token from BOT_TOKEN or TELEGRAM_BOT_TOKEN."""
    load_env_file()
    token = (
        os.environ.get("BOT_TOKEN", "")
        or os.environ.get("TELEGRAM_BOT_TOKEN", "")
    ).strip()
    if not token:
        raise SystemExit(
            "No bot token found. Set BOT_TOKEN (or TELEGRAM_BOT_TOKEN) "
            "as an environment variable, or create a .env file "
            "(see .env.example)."
        )
    return token
