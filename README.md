# Bob 🤖

Bob is a friendly Telegram bot that helps manage your groups. It greets new members, says goodbye to leavers, translates non-English messages, transcribes voice messages, and gives admins tools to keep their groups tidy.

## Features

- **Welcome & farewell messages** — customizable per group, with `%groupname%` and `<name>` placeholders
- **Ban** — admins can ban members by replying to a message or mentioning a user
- **Promote / demote** — admins can promote other admins (and undo it)
- **Auto-translation** — non-English group messages are translated to English via OpenRouter (optional)
- **Voice transcription** — voice messages are transcribed locally with Whisper and replied as text
- **Broadcast** — the bot owner can send one message to every group Bob is in (groups can opt out)

## Commands

| Command | What it does | Who can use it |
|---|---|---|
| `/start` | Shows setup info / activates Bob in a group | Anyone |
| `/help` | Shows the command list | Anyone |
| `/welcomemsg <msg>` | Sets the group welcome message (`default` to reset) | Admins |
| `/farewellmsg <msg>` | Sets the group farewell message (`default` to reset) | Admins |
| `/ban` | Bans the user you reply to or mention | Admins |
| `/premote` (or `/promote`) | Promotes an admin to full admin rights | Admins |
| `/demote` | Demotes an admin back to a member | Admins |
| `/broadcastoff` | Toggles whether this group receives broadcasts | Admins |
| `/broadcast <msg>` | Sends the message to every group Bob is in | Bot owner |

## Setup

1. **Create a bot**: talk to [@BotFather](https://t.me/BotFather), use `/newbot`, and copy the token.
2. **Install**: `pip install -r requirements.txt`
3. **Configure**: copy `.env.example` to `.env` and set `BOT_TOKEN` (and optionally the other values).
4. **Run**: `python bob.py`

Add Bob to a group, make it an admin (it needs **Change group info** for messages, and **Ban users** / **Promote members** for moderation commands), and type `/start` in the group.

## Configuration

| Variable | Required | Description |
|---|---|---|
| `BOT_TOKEN` | ✅ | Token from @BotFather |
| `OPENROUTER_API_KEY` | — | Enables auto-translation |
| `OPENROUTER_MODEL` | — | OpenRouter model id (default `openrouter/free`) |
| `TRANSLATE_COOLDOWN_SECONDS` | — | Min seconds between translations per chat (default 15) |
| `BOT_OWNER_USER_ID` | — | Your Telegram user ID; enables `/broadcast` |
| `WHISPER_MODEL` | — | Whisper model size: `tiny`, `base`, `small`, `medium`, `large` (default `base`) |

## Deployment

- **VPS**: clone the repo, install requirements, set up `.env`, and run `python bob.py` (e.g. under `tmux` or `systemd`).
- **JustRunMy.App**: see [JUSTRUNMY.md](JUSTRUNMY.md) — zip the project with `build_zip.ps1` and upload it.

## License

[MIT](LICENSE)