import os
import logging
import requests
from urllib.parse import quote_plus
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables required:
# TELEGRAM_TOKEN - your bot token from BotFather
# DEEPAI_API_KEY - API key for https://deepai.org image recognition
# AFFILIATE_TAG - your Amazon Associates tag

DEEPAI_API_URL = "https://api.deepai.org/api/densecap"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Send me a product image and I'll try to find it on Amazon!")


def recognize_image(path: str, api_key: str):
    """Send image to DeepAI for recognition and return a list of tags."""
    headers = {"api-key": api_key}
    with open(path, "rb") as f:
        response = requests.post(DEEPAI_API_URL, files={"image": f}, headers=headers, timeout=30)
    response.raise_for_status()
    data = response.json()
    # Extract tags from DeepAI densecap result
    tags = []
    for item in data.get("output", {}).get("captions", []):
        caption = item.get("caption")
        if caption:
            tags.append(caption)
    return tags


def build_affiliate_link(keyword: str, affiliate_tag: str) -> str:
    """Create a simple Amazon search link with affiliate tag."""
    query = quote_plus(keyword)
    return f"https://www.amazon.com/s?k={query}&tag={affiliate_tag}"


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    bot = context.bot
    api_key = os.environ.get("DEEPAI_API_KEY")
    affiliate_tag = os.environ.get("AFFILIATE_TAG")
    if not api_key or not affiliate_tag:
        await update.message.reply_text("Bot not configured properly. Missing API keys.")
        return

    # Get the highest resolution photo
    photo = update.message.photo[-1]
    file = await bot.get_file(photo.file_id)
    file_path = os.path.join("/tmp", f"{photo.file_unique_id}.jpg")
    await file.download_to_drive(file_path)
    logger.info("Image downloaded to %s", file_path)

    try:
        tags = recognize_image(file_path, api_key)
    except Exception as e:
        logger.error("Image recognition failed: %s", e)
        await update.message.reply_text("Sorry, I couldn't analyze that image.")
        return
    finally:
        try:
            os.remove(file_path)
        except OSError:
            pass

    if not tags:
        await update.message.reply_text("No recognizable objects found.")
        return

    # Use the first tag to build an affiliate link
    keyword = tags[0]
    link = build_affiliate_link(keyword, affiliate_tag)
    await update.message.reply_text(f"I found: {keyword}\n{link}")


async def main() -> None:
    token = os.environ.get("TELEGRAM_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_TOKEN environment variable not set")

    application = ApplicationBuilder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    logger.info("Bot started")
    await application.run_polling()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
