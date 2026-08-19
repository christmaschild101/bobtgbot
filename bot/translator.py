"""Language detection and OpenRouter-powered translation for Bob."""

from __future__ import annotations

import logging
from typing import Optional

import httpx
from langdetect import DetectorFactory, LangDetectException, detect_langs

from .config import get_openrouter_key, get_openrouter_model

logger = logging.getLogger(__name__)

# Deterministic results from langdetect.
DetectorFactory.seed = 0

TRANSLATION_PROMPT = (
    "Please do the folowing to the folowing message. "
    "1. Detect what language it is from. "
    "2. Translate it to English. "
    "3. Send it back, just the translation. "
    "NO long message, no here is the translation, just the translation."
)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# langdetect is unreliable on very short input.
MIN_DETECT_LENGTH = 4


def _normalize(text: str) -> str:
    """Lowercase and strip punctuation/whitespace for echo detection."""
    return "".join(ch for ch in text.lower() if ch.isalnum())


def detect_language(text: str) -> Optional[str]:
    """Return the top language code of the text, or None if undetectable.

    Only the top candidate is used; short or ambiguous English can still be
    mislabeled, so callers should pair this with `is_echo()` before replying.
    """
    if not text or len(text.strip()) < MIN_DETECT_LENGTH:
        return None
    try:
        langs = detect_langs(text.strip())
    except LangDetectException:
        return None
    if not langs:
        return None
    return langs[0].lang


def is_echo(original: str, translation: str) -> bool:
    """Return True when the 'translation' is really just the original text."""
    return _normalize(original) == _normalize(translation)


def build_prompt(message: str) -> str:
    """Return the exact translation prompt with the message appended."""
    return f"{TRANSLATION_PROMPT}\n\n{message}"


async def translate_to_english(text: str) -> Optional[str]:
    """Translate text to English via OpenRouter. Returns None on any failure."""
    api_key = get_openrouter_key()
    if not api_key:
        return None

    payload = {
        "model": get_openrouter_model(),
        "messages": [{"role": "user", "content": build_prompt(text)}],
        "temperature": 0.3,
        "max_tokens": 2048,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(OPENROUTER_URL, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
        content = data["choices"][0]["message"]["content"]
    except (httpx.HTTPError, KeyError, IndexError, TypeError) as exc:
        logger.warning("OpenRouter translation failed: %s", exc)
        return None

    translation = content.strip()
    return translation or None