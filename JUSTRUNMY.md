# Deploy Bob to JustRunMy.App (Zip method)

This zip contains everything JustRunMy needs. No token is inside it - set it as
an environment variable in their panel.

## Steps

1. Go to https://justrunmy.app and sign in / register (no credit card).
2. Create a new app and choose the **Zip** deployment method.
3. Pick a **Python** base image.
4. Upload `bob-justrunmy.zip`.
5. Add an environment variable:
   - Key: `BOT_TOKEN` (or `TELEGRAM_BOT_TOKEN`)
   - Value: your token from @BotFather
6. Set the startup command to:
   ```
   python bob.py
   ```
7. Start the app, open the logs, and look for `Bob is starting...`.

## Notes

- No exposed port is needed - Bob uses long polling, so it works out of the box.
- Settings are saved to `bob_data.json` in the project folder and persist
  across restarts.
- If you update the code, just re-upload a fresh zip and restart the app.
- Never put your real token in the zip or in `bob.py`. Use the env var only.