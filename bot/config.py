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


def get_openrouter_key() -> str:
    """Return the OpenRouter API key, or "" if not configured."""
    load_env_file()
    return os.environ.get("OPENROUTER_API_KEY", "").strip()


def get_openrouter_model() -> str:
    """Return the OpenRouter model id, defaulting to the free auto-router."""
    load_env_file()
    return os.environ.get("OPENROUTER_MODEL", "").strip() or "openrouter/free"


def get_translate_cooldown() -> float:
    """Return the minimum seconds between translations per chat."""
    load_env_file()
    try:
        return float(os.environ.get("TRANSLATE_COOLDOWN_SECONDS", "15"))
    except ValueError:
        return 15.0



def get_bot_owner() -> int | None:
    """Return the bot owner's Telegram user ID, or None if not configured."""
    load_env_file()
    raw = os.environ.get("BOT_OWNER_USER_ID", "").strip()
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        return None


def get_whisper_model() -> str:
    """Return the Whisper model size, defaulting to 'base'.

    Set the WHISPER_MODEL env var to 'tiny', 'base', 'small', 'medium',
    or 'large' to override.
    """
    load_env_file()
    return os.environ.get("WHISPER_MODEL", "base").strip() or "base"
