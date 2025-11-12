import os
import asyncio
import datetime
from flask import Flask
from telegram.ext import Application

# ================= Настройки =================
TOKEN = os.getenv("BOT_TOKEN")  # токен бота
CHAT_ID = os.getenv("CHAT_ID")  # ID чата для уведомлений

if not TOKEN or not CHAT_ID:
    raise ValueError("Не установлены переменные окружения BOT_TOKEN или CHAT_ID")

# ================= Telegram =================
application = Application.builder().token(TOKEN).build()

# ================= Flask =================
app = Flask(__name__)  # Gunicorn ищет эту переменную

# ================= Функция уведомления =================
async def send_test_reminder():
    text = (
        "🥦 Тестовое уведомление! Бот работает и может отправлять напоминания."
    )
    try:
        await application.bot.send_message(chat_id=CHAT_ID, text=text)
        print(f"✅ Уведомление отправлено {datetime.datetime.now()}")
    except Exception as e:
        print(f"❌ Ошибка отправки уведомления: {e}")

# ================= Роут Flask =================
@app.route("/", methods=["GET"])
def index():
    asyncio.run(send_test_reminder())
    return "Тестовое уведомление отправлено ✅", 200

# ================= Локальный запуск =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
