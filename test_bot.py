import os
import asyncio
from telegram.ext import Application
import datetime

# ================= Настройки =================
TOKEN = os.getenv("BOT_TOKEN")  # токен бота
CHAT_ID = os.getenv("CHAT_ID")  # куда отправлять уведомления

if not TOKEN or not CHAT_ID:
    raise ValueError("Не установлены переменные окружения BOT_TOKEN или CHAT_ID")

# ================= Telegram =================
application = Application.builder().token(TOKEN).build()

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

# ================= Запуск =================
if __name__ == "__main__":
    asyncio.run(send_test_reminder())
