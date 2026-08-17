"""Bob - a Telegram bot for managing groups."""

from .config import get_token
from .storage import BobStore

__all__ = ["get_token", "BobStore"]