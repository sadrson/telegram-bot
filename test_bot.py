import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ================= Настройки =================
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")  # можно использовать для теста
if not TOKEN:
    raise ValueError("Не установлен BOT_TOKEN")
if not CHAT_ID:
    raise ValueError("Не установлен CHAT_ID")

# ================= Telegram =================
application = Application.builder().token(TOKEN).build()

# ======== Обработчики команд ========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! 🥦 Я бот для тестирования уведомлений. "
        "Я могу присылать напоминания и уведомления."
    )

application.add_handler(CommandHandler("start", start))

# ================= Flask =================
app = Flask(__name__)

# ======== Отправка тестового уведомления ========
async def send_test_message(chat_id: str):
    await application.bot.send_message(chat_id=chat_id, text="🥦 Тестовое уведомление! Бот работает ✅")

# ======== Роут для теста через браузер ========
@app.route("/", methods=["GET"])
async def index():
    await send_test_message(CHAT_ID)
    return "Тестовое уведомление отправлено ✅", 200

# ======== Роут для webhook ========
@app.route("/webhook", methods=["POST"])
async def webhook():
    data = await request.get_json()
    if not data:
        return {"ok": False, "error": "Empty request"}, 400

    update = Update.de_json(data, application.bot)
    await application.update_queue.put(update)
    return {"ok": True}, 200

# ================= Локальный запуск =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"Запуск на порту {port}...")
    app.run(host="0.0.0.0", port=port)
