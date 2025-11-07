from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import os
import asyncio

# === Настройки ===
TOKEN = os.getenv("BOT_TOKEN")
app = Flask(__name__)

# === Инициализация Telegram Application ===
application = Application.builder().token(TOKEN).build()
loop = asyncio.get_event_loop()

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
    """Приём апдейтов от Telegram"""
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, application.bot)

        async def process_update():
            try:
                if not application._initialized:
                    await application.initialize()
                await application.process_update(update)
            except Exception as e:
                print(f"Async error: {e}")

        # запускаем обработку асинхронно, не блокируя ответ Telegram
        asyncio.run_coroutine_threadsafe(process_update(), loop)

    except Exception as e:
        print(f"Webhook error: {e}")

    # Telegram сразу получает ответ, не дожидаясь обработки
    return jsonify({"ok": True}), 200


# === Главная страница ===
@app.route("/", methods=["GET"])
def home():
    return "Бот запущен 🚀", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
