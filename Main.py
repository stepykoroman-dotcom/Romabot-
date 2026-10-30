
import os
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from openai import OpenAI

TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
OPENAI_KEY = os.environ["OPENAI_API_KEY"]

client = OpenAI(api_key=OPENAI_KEY)

logging.basicConfig(level=logging.INFO)

# Сюда добавим Telegram ID близких
ALLOWED_USERS = set()

SYSTEM_PROMPT = """
Ты — цифровой помощник Ромы.
Общайся естественно, неформально, с юмором.
Используй русский язык, допускай разговорные выражения
и мат, если это уместно.
Не утверждай, что ты сам Рома.
Если спрашивают, объясняй, что ты его ИИ-помощник.
Не выдумывай факты о Роме.
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    await update.message.reply_text(
        f"Привет! Я цифровой помощник Ромы.\n"
        f"Твой Telegram ID: {user_id}"
    )

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if ALLOWED_USERS and user_id not in ALLOWED_USERS:
        await update.message.reply_text("У тебя пока нет доступа.")
        return

    message = update.message.text

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            instructions=SYSTEM_PROMPT,
            input=message
        )

        await update.message.reply_text(response.output_text)

    except Exception:
        logging.exception("Ошибка OpenAI")
        await update.message.reply_text(
            "Что-то пошло не так. Попробуй ещё раз."
        )

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, chat)
    )

    app.run_polling(
    bootstrap_retries=-1,
    timeout=30,
    read_timeout=30,
    write_timeout=30,
    connect_timeout=30,
    pool_timeout=30
)


if __name__ == "__main__":
    main()

