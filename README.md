# Tele-bots-
A collection of different telegram bots

## Affiliate Bot

`affiliate_bot` contains a simple Telegram bot that analyses a product image
using the [DeepAI](https://deepai.org) image recognition API and returns an
Amazon search link with your affiliate tag.

### Setup

1. Install requirements
   ```bash
   pip install -r affiliate_bot/requirements.txt
   ```
2. Create a bot with [BotFather](https://t.me/BotFather) and note the token.
3. Export the following environment variables before running the bot:
   - `TELEGRAM_TOKEN` – the token from BotFather
   - `DEEPAI_API_KEY` – your DeepAI API key
   - `AFFILIATE_TAG` – your Amazon Associates tag

### Running

```bash
python affiliate_bot/bot.py
```

Send a photo of a product to the bot and it will reply with the first object
caption detected by DeepAI and a corresponding Amazon search link that includes
your affiliate tag.
