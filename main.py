import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN", "8274488039:AAEBT6A-NSFMINjrM1ZboPg8Iq7Eh-K-XK0")

app = Flask(__name__)

# Создаем Telegram Application
application = Application.builder().token(TOKEN).build()


# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Бот работает 🚀")


# Эхо сообщений
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Ты написал: {update.message.text}")


# Регистрируем обработчики
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))


# Flask endpoint для Telegram webhook
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)

    # Асинхронно инициализируем и обрабатываем update
    asyncio.run(run_update(update))
    return "ok", 200


async def run_update(update: Update):
    if not application._initialized:
        await application.initialize()
    await application.process_update(update)


@app.route("/")
def home():
    return "Bot is running!", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
