from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, filters
import os

# === Настройки ===
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(TOKEN)

# === Flask-приложение ===
app = Flask(__name__)

# === Dispatcher (обработка обновлений Telegram) ===
dispatcher = Dispatcher(bot, None, workers=0)

def start(update, context):
    update.message.reply_text("✅ Бот успешно работает на Render!")

def echo(update, context):
    update.message.reply_text(update.message.text)

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# === Webhook endpoint — должен совпадать с setWebhook ===
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok", 200

# === Проверочный маршрут (для браузера) ===
@app.route("/", methods=["GET"])
def home():
    return "Бот запущен 🚀", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
