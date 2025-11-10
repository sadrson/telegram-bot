from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import os
import asyncio
import threading
import logging

# === Настройки ===
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден!")

RENDER_HOST = os.getenv("RENDER_EXTERNAL_HOSTNAME")
if not RENDER_HOST:
    raise ValueError("❌ RENDER_EXTERNAL_HOSTNAME не найден!")

app = Flask(__name__)

# === Логирование ===
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# === Telegram Application ===
application = Application.builder().token(TOKEN).build()


# === Обработчики ===
async def start(update: Update, context):
    await update.message.reply_text("✅ Бот успешно работает на Render!")


async def echo(update: Update, context):
    await update.message.reply_text(update.message.text)


application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))


# === Фоновый запуск Telegram-приложения ===
def run_telegram():
    loop = asyncio.new_event_loop()      # создаём новый event loop
    asyncio.set_event_loop(loop)         # устанавливаем его для текущего потока
    loop.run_until_complete(application.initialize())
    loop.run_until_complete(application.start())
    logger.info("✅ Telegram application started (background mode)")
    loop.run_forever()


threading.Thread(target=run_telegram, daemon=True).start()


# === Webhook endpoint ===
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, application.bot)
        asyncio.run(application.process_update(update))
    except Exception as e:
        logger.error(f"Ошибка в webhook: {e}", exc_info=True)
    return jsonify({"ok": True}), 200


# === Главная страница ===
@app.route("/", methods=["GET"])
def home():
    return "Бот запущен 🚀", 200


# === Установка вебхука ===
@app.route("/set_webhook", methods=["GET"])
def set_webhook():
    webhook_url = f"https://{RENDER_HOST}/webhook"
    try:
        asyncio.run(application.bot.set_webhook(webhook_url))
        logger.info(f"Webhook установлен: {webhook_url}")
        return jsonify({"ok": True, "webhook": webhook_url})
    except Exception as e:
        logger.error(f"Ошибка при установке webhook: {e}", exc_info=True)
        return jsonify({"ok": False, "error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
