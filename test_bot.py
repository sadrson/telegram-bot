from flask import Flask, request
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler

# === Flask app ===
app = Flask(__name__)

# === Telegram Bot ===
TOKEN = "<YOUR_BOT_TOKEN>"  # <-- вставь сюда свой токен
application = ApplicationBuilder().token(TOKEN).build()

# Инициализируем приложение (обязательно)
application.initialize()

# === Хэндлеры ===
async def start(update: Update, context):
    await update.message.reply_text("Бот работает 🚀")

application.add_handler(CommandHandler("start", start))

# === Webhook endpoint ===
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)

    # Получаем текущий loop и запускаем корутину
    loop = asyncio.get_event_loop()
    asyncio.run_coroutine_threadsafe(application.process_update(update), loop)

    return "OK", 200

# === Для локального теста ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
