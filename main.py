from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import os

TOKEN = os.getenv("BOT_TOKEN", "8274488039:AAEBT6A-NSFMINjrM1ZboPg8Iq7Eh-K-XK0")

app = Flask(__name__)

# создаём Telegram приложение
telegram_app = Application.builder().token(TOKEN).build()


# обработчик /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Бот запущен и работает 🚀")


# обработчик обычных сообщений
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Ты написал: {update.message.text}")


# добавляем хендлеры
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))


# Flask webhook endpoint
@app.route("/webhook", methods=["POST"])
async def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return "ok", 200


@app.route("/")
def home():
    return "Bot is running!", 200


if __name__ == "__main__":
    # запуск Flask (локально)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
