"""Command and event handlers for Bob."""

from __future__ import annotations

import asyncio
import time
from typing import Optional

from telegram import Chat, Update, User
from telegram.constants import ChatMemberStatus, ChatType
from telegram.error import BadRequest, Forbidden, TelegramError
from telegram.ext import ContextTypes

from .storage import BobStore
from .translator import detect_language, is_echo, translate_to_english

HELP_TEXT = (
    "Bob helps keep your group friendly. Available commands:\n\n"
    "/start - setup info\n"
    "/help - this message\n"
    "/welcomemsg <msg> - set the welcome message (admins). "
    "Use \"default\" to reset.\n"
    "/farewellmsg <msg> - set the goodbye message (admins). "
    "Use \"default\" to reset.\n"
    "/ban - ban the user you reply to (admins)\n\n"
    "Placeholders: %groupname% in the welcome message, "
    "<name> in the goodbye message."
)


async def is_admin(update: Update, user_id: int) -> bool:
    """Return True if the user is an owner or administrator of the chat."""
    chat = update.effective_chat
    if chat is None:
        return False
    try:
        member = await chat.get_member(user_id)
    except TelegramError:
        return False
    return member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)


def _render(text: str, chat: Chat, user: Optional[User] = None) -> str:
    """Substitute placeholders in a stored message."""
    group = chat.title or "the group"
    name = user.full_name if user else "someone"
    rendered = text.replace("%groupname%", group)
    rendered = rendered.replace("<name>", name)
    rendered = rendered.replace("%name%", name)
    return rendered


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    if chat is None or update.effective_message is None:
        return
    store: BobStore = context.bot_data["store"]

    if chat.type == ChatType.PRIVATE:
        username = context.bot.username or "the bot"
        text = (
            f"Hi! I'm Bob. I help manage groups.\n\n"
            f"To set me up:\n"
            f"1. Open the group you want me in.\n"
            f"2. Add me to it by searching for @{username} "
            f"(Add members -> search \"{username}\").\n"
            f"3. Type /start in the group so I activate.\n\n"
            f"Then use /help to see what I can do."
        )
        await update.effective_message.reply_text(text)
        return

    store.get_welcome(chat.id)
    await update.effective_message.reply_text(
        f"Bob is active in {chat.title or 'this group'}! Type /help to see commands."
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if message is not None:
        await message.reply_text(HELP_TEXT)


def _parse_set_msg(args: list[str], keyword: str) -> tuple[Optional[str], Optional[str]]:
    """Return (new_message, error_message)."""
    if not args:
        return None, f"Usage: /{keyword} <message> or /{keyword} default"
    if len(args) == 1 and args[0].lower() == "default":
        return None, None  # sentinel handled by caller as "reset to default"
    return " ".join(args).strip(), None


async def cmd_set_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _set_message(update, context, kind="welcome")


async def cmd_set_farewell(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _set_message(update, context, kind="farewell")


async def _set_message(
    update: Update, context: ContextTypes.DEFAULT_TYPE, kind: str
) -> None:
    chat = update.effective_chat
    message = update.effective_message
    if chat is None or message is None:
        return
    store: BobStore = context.bot_data["store"]

    if chat.type == ChatType.PRIVATE:
        await message.reply_text("Run this command inside the group instead.")
        return

    if not await is_admin(update, update.effective_user.id):
        await message.reply_text("Only admins can change that.")
        return

    command = "welcomemsg" if kind == "welcome" else "farewellmsg"
    text, error = _parse_set_msg(context.args, command)
    if error:
        await message.reply_text(error)
        return

    if text is None:
        # "default" was passed -> reset
        if kind == "welcome":
            from .storage import DEFAULT_WELCOME

            store.set_welcome(chat.id, DEFAULT_WELCOME)
        else:
            from .storage import DEFAULT_FAREWELL

            store.set_farewell(chat.id, DEFAULT_FAREWELL)
        await message.reply_text(f"{command}: back to the default message.")
        return

    if kind == "welcome":
        store.set_welcome(chat.id, text)
        preview = _render(text, chat)
    else:
        store.set_farewell(chat.id, text)
        preview = _render(text, chat, user=None)
    await message.reply_text(f"{command} updated. Preview:\n{preview}")


async def cmd_ban(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    message = update.effective_message
    if chat is None or message is None:
        return

    if chat.type == ChatType.PRIVATE:
        await message.reply_text("Run this command inside the group instead.")
        return

    if not await is_admin(update, update.effective_user.id):
        await message.reply_text("Only admins can ban people.")
        return

    target = _resolve_target(update, context.args)
    if target is None:
        await message.reply_text(
            "Reply to the person you want to ban, or pass an ID / @username."
        )
        return

    if target.id == context.bot.id:
        await message.reply_text("Nice try.")
        return

    try:
        await context.bot.ban_chat_member(chat.id, target.id)
    except Forbidden:
        await message.reply_text(
            "I can't ban people - make me an admin first."
        )
        return
    except BadRequest as exc:
        await message.reply_text(f"Couldn't ban: {exc.message or 'bad request'}.")
        return

    name = target.full_name or str(target.id)
    await message.reply_text(f"Bye bye, {name}. Banned.")


def _resolve_target(
    update: Update, args: list[str] | None
) -> Optional[User]:
    """Resolve the user to ban from reply, mention entity, or args."""
    message = update.effective_message
    if message is None:
        return None

    if message.reply_to_message is not None:
        user = message.reply_to_message.from_user
        if user is not None:
            return user

    for entity in message.entities or []:
        if entity.type in ("text_mention", "mention") and entity.user is not None:
            return entity.user

    if args:
        for token in args:
            token = token.strip().lstrip("@")
            if token.isdigit():
                return User(id=int(token), first_name="", is_bot=False)
    return None


async def on_new_members(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    message = update.effective_message
    if chat is None or message is None or message.new_chat_members is None:
        return
    store: BobStore = context.bot_data["store"]

    for member in message.new_chat_members:
        if member.id == context.bot.id:
            store.get_welcome(chat.id)
            await message.reply_text(
                "Thanks for adding me! Type /help to see what I can do."
            )
            continue
        welcome = store.get_welcome(chat.id)
        await message.reply_text(_render(welcome, chat, member))


async def on_left_member(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    message = update.effective_message
    if chat is None or message is None or message.left_chat_member is None:
        return
    store: BobStore = context.bot_data["store"]
    farewell = store.get_farewell(chat.id)
    await message.reply_text(_render(farewell, chat, message.left_chat_member))


async def on_translatable_message(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Translate non-English group messages via OpenRouter."""
    if not context.bot_data.get("translator_enabled"):
        return
    chat = update.effective_chat
    message = update.effective_message
    if chat is None or message is None or not message.text:
        return
    sender = message.from_user
    if sender is None or sender.is_bot:
        return

    cooldown = float(context.bot_data.get("translate_cooldown", 15.0))
    now = time.monotonic()
    last = context.chat_data.get("last_translation")
    if last is not None and now - last < cooldown:
        return

    language = await asyncio.to_thread(detect_language, message.text)
    if language is None or language == "en":
        return

    translation = await translate_to_english(message.text)
    if not translation:
        return
    if is_echo(message.text, translation):
        return

    context.chat_data["last_translation"] = time.monotonic()
    await message.reply_text(translation)