import os
import logging
from google import genai
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
GEMINI_KEY = os.environ["GEMINI_API_KEY"]

client = genai.Client(api_key=GEMINI_KEY)

ALLOWED_USERS = set()
histories = {}

SYSTEM_PROMPT = """
Ты — ИИ-помощник Ромы.
Общайся на русском языке, естественно и неформально.
Используй юмор и разговорные выражения.
Не выдавай себя за настоящего Рому.
Если спрашивают, честно говори, что ты его ИИ-помощник.
Не выдумывай факты о Роме.
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text(
        "Привет! Я цифровой помощник Ромы. "
        f"Твой Telegram ID: {user_id}"
    )

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in ALLOWED_USERS:
        await update.message.reply_text("У тебя пока нет доступа.")
        return

    message = update.message.text
    history = histories.setdefault(user_id, [])

    try:
        response = client.interactions.create(
            model="gemini-3.8-flash",
            input=history + [{"role": "user", "content": message}],
            system_instruction=SYSTEM_PROMPT
        )

        answer = response.output_text

        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": answer})
        histories[user_id] = history[-20:]

        await update.message.reply_text(answer)

    except Exception:
        logging.exception("Ошибка Gemini")
        await update.message.reply_text(
            "Что-то пошло не так. Попробуй ещё раз."
        )

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, chat)
    )
    app.run_polling()

if __name__ == "__main__":
    main()

