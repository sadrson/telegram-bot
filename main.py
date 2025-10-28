from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import os
import asyncio

# === Настройки ===
TOKEN = os.getenv("BOT_TOKEN")

# === Flask-приложение ===
app = Flask(__name__)

# === Telegram Application ===
application = Application.builder().token(TOKEN).build()

# === Команды ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Бот успешно работает на Render!")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(update.message.text)

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# === Webhook endpoint ===
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    asyncio.run(application.process_update(update))
    return "ok", 200

# === Проверочный маршрут ===
@app.route("/", methods=["GET"])
def home():
    return "Бот запущен 🚀", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app
