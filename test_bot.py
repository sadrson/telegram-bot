import os
import asyncio
from telegram.ext import Application
import datetime

# ================= Настройки =================
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")  # куда отправлять уведомления

# ================= Telegram =================
application = Application.builder().token(TOKEN).build()

# ================= Функция уведомления =================
async def send_test_reminder():
    if not CHAT_ID:
        print("❌ CHAT_ID не установлен!")
        return

    text = (
        "🥦 Тестовое уведомление! Бот работает и может отправлять напоминания."
    )
    try:
        await application.bot.send_message(chat_id=CHAT_ID, text=text)
        print(f"✅ Уведомление отправлено {datetime.datetime.now()}")
    except Exception as e:
        print(f"Ошибка отправки уведомления: {e}")

# ================= Запуск =================
async def main():
    await send_test_reminder()

if __name__ == "__main__":
    asyncio.run(main())
