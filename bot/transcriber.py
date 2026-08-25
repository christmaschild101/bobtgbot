"""Local voice-message transcription using OpenAI Whisper + FFmpeg."""

from __future__ import annotations

import asyncio
import logging
import tempfile
from pathlib import Path
from typing import Optional

import whisper

from .config import get_whisper_model

logger = logging.getLogger(__name__)

_model: Optional[whisper.Whisper] = None
_model_lock = asyncio.Lock()


def _load_model() -> whisper.Whisper:
    """Return the cached Whisper model, loading it on first call."""
    global _model
    if _model is None:
        name = get_whisper_model()
        logger.info("Loading Whisper model %r (first voice message)…", name)
        _model = whisper.load_model(name)
    return _model


async def transcribe_voice(file_bytes: bytes) -> Optional[str]:
    """Transcribe a Telegram voice message (OGA) and return the text.

    Returns ``None`` on any failure.  The heavy work runs in a thread so
    the event loop stays responsive.
    """
    tmp = Path(tempfile.gettempdir()) / f"bob_voice_{id(file_bytes)}.oga"
    try:
        tmp.write_bytes(file_bytes)

        def _run() -> str:
            model = _load_model()
            result = model.transcribe(str(tmp), fp16=False)
            return result["text"].strip()

        text = await asyncio.to_thread(_run)
        return text or None
    except Exception:
        logger.exception("Whisper transcription failed")
        return None
    finally:
        tmp.unlink(missing_ok=True)
