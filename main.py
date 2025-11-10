from flask import Flask, request, jsonify
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import os
import asyncio
import threading
import signal
import sys

# === Настройки ===
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # https://your-app.onrender.com/webhook
PORT = int(os.environ.get("PORT", 10000))

app = Flask(__name__)

# === Telegram Application ===
application = Application.builder().token(TOKEN).build()

# Глобальный event loop
loop = asyncio.new_event_loop()

def start_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

threading.Thread(target=start_loop, args=(loop,), daemon=True).start()

# === Graceful shutdown ===
shutdown_event = threading.Event()

def handle_shutdown(sig, frame):
    print("SIGTERM получен, закрываемся...")
    shutdown_event.set()
    Bot(TOKEN).delete_webhook()
    sys.exit(0)

signal.signal(signal.SIGTERM, handle_shutdown)
signal.signal(signal.SIGINT, handle_shutdown)

# === Обработчики ===
async def start(update: Update, context):
    await update.message.reply_text("✅ Бот успешно работает на Render!")

async def echo(update: Update, context):
    await update.message.reply_text(update.message.text)

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# === Webhook endpoint ===
@app.route("/webhook", methods=["POST"])
def webhook():
    if shutdown_event.is_set():
        return jsonify({"ok": True, "message": "Shutting down"}), 200

    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)

    # Отправляем обработку апдейта в глобальный loop
    asyncio.run_coroutine_threadsafe(application.process_update(update), loop)

    return jsonify({"ok": True}), 200

# === Главная страница для проверки ===
@app.route("/", methods=["GET"])
def home():
    return "Бот запущен 🚀", 200

# === Установка webhook при старте ===
def set_webhook():
    bot = Bot(TOKEN)
    bot.set_webhook(url=WEBHOOK_URL, max_connections=1)
    print("Webhook установлен!")

if __name__ == "__main__":
    set_webhook()
    app.run(host="0.0.0.0", port=PORT)
