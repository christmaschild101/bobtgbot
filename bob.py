"""Bob - a Telegram bot for managing groups.

Run with:  python bob.py
"""

from __future__ import annotations

import logging
from pathlib import Path

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)

from bot.handlers import (
    cmd_ban,
    cmd_help,
    cmd_set_farewell,
    cmd_set_welcome,
    cmd_start,
    on_left_member,
    on_new_members,
    on_translatable_message,
)
from bot.storage import BobStore

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

DATA_FILE = Path(__file__).resolve().parent / "bob_data.json"

def build_application() -> Application:
    store = BobStore(DATA_FILE)
    app = Application.builder().token(get_token()).build()
    app.bot_data["store"] = store
    app.bot_data["translator_enabled"] = bool(get_openrouter_key())
    app.bot_data["translate_cooldown"] = get_translate_cooldown()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))

    # welcome / goodbye (farewellmsg + the user's "fairwellmsg" spelling)
    app.add_handler(CommandHandler("welcomemsg", cmd_set_welcome))
    app.add_handler(CommandHandler("farewellmsg", cmd_set_farewell))
    app.add_handler(CommandHandler("fairwellmsg", cmd_set_farewell))

    app.add_handler(CommandHandler("ban", cmd_ban))

    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, on_new_members))
    app.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, on_left_member))
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND & filters.ChatType.GROUPS,
            on_translatable_message,
        )
    )

    app.add_handler(
    )

    return app

def main() -> None:
    app = build_application()
    logger.info("Bob is starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()