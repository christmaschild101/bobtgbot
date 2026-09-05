"""Local voice-message transcription using faster-whisper + FFmpeg."""

from __future__ import annotations

import asyncio
import logging
import tempfile
from pathlib import Path
from typing import Any, Optional

from .config import get_whisper_model

logger = logging.getLogger(__name__)

_model: Any = None


def _load_model() -> Any:
    """Return the cached WhisperModel, loading it on first call."""
    global _model
    if _model is None:
        try:
            from faster_whisper import WhisperModel
        except ImportError:
            raise ImportError(
                "faster-whisper is not installed. "
                "Run: pip install faster-whisper"
            )
        name = get_whisper_model()
        logger.info("Loading Whisper model %r (first voice message)...", name)
        _model = WhisperModel(name, device="cpu", compute_type="int8")
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
            segments, _info = model.transcribe(str(tmp))
            return "".join(seg.text for seg in segments).strip()

        text = await asyncio.to_thread(_run)
        return text or None
    except ImportError:
        logger.error("faster-whisper is not installed - transcription disabled")
        return None
    except Exception:
        logger.exception("Whisper transcription failed")
        return None
    finally:
        tmp.unlink(missing_ok=True)
