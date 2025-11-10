from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import os
import asyncio
import logging

# === Настройки ===
TOKEN = os.getenv("BOT_TOKEN")
app = Flask(__name__)

# === Логирование ===
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# === Telegram Application ===
application = Application.builder().token(TOKEN).build()
loop = asyncio.get_event_loop()

# === Обработчики ===
async def start(update: Update, context):
    user = update.effective_user
    logger.info(f"Команда /start от {user.id} ({user.first_name})")
    await update.message.reply_text("✅ Бот успешно работает на Render!")

async def echo(update: Update, context):
    user = update.effective_user
    message = update.message.text
    logger.info(f"Сообщение от {user.id} ({user.first_name}): {message}")
    await update.message.reply_text(message)

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# === Webhook endpoint ===
@app.route("/webhook", methods=["POST"])
def webhook():
    """Приём апдейтов от Telegram"""
    try:
        data = request.get_json(force=True)
        logger.info(f"Получен update: {data}")
        update = Update.de_json(data, application.bot)

        async def process_update():
            if not application._initialized:
                await application.initialize()
            await application.process_update(update)

        loop.create_task(process_update())

    except Exception as e:
        logger.error(f"Ошибка в webhook: {e}", exc_info=True)

    return jsonify({"ok": True}), 200

# === Главная страница ===
@app.route("/", methods=["GET"])
def home():
    return "Бот запущен 🚀", 200

# === Запуск ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"Запуск Flask на порту {port}")
    app.run(host="0.0.0.0", port=port)
