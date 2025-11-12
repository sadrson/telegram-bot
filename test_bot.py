import os
import asyncio
import pytz
from datetime import datetime
from flask import Flask, request
from telegram import Bot

# === Конфигурация ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=BOT_TOKEN)
app = Flask(__name__)

# === Главная страница ===
@app.route("/")
def index():
    return "Bot is running", 200

# === Webhook обработчик ===
@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json()
    print("Webhook received:", update)
    return "ok", 200

# === Маршрут для отправки сообщения вручную или по cron ===
@app.route("/send", methods=["POST", "GET"])
def send_message():
    chat_id = CHAT_ID
    text = (
        "🥦 Напоминание! Не забудь заполнить "
        "[форму](https://docs.google.com/forms/d/e/1FAIpQLSeG38n-P76ju46Zi6D4CHX8t6zfbxN506NupZboNeERhkT81A/viewform)"
    )

    try:
        asyncio.run(bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown"))
        print(f"✅ Уведомление отправлено пользователю {chat_id}")
        return "Message sent", 200
    except Exception as e:
        print("Ошибка при отправке:", e)
        return str(e), 500

# === Тест: автоматическое уведомление по расписанию (среда, пятница, воскресенье 15:00 UTC+5) ===
async def schedule_task():
    tz = pytz.timezone("Asia/Yekaterinburg")  # UTC+5
    while True:
        now = datetime.now(tz)
        day = now.strftime("%a")  # Wed, Fri, Sun
        time_str = now.strftime("%H:%M")

        if day in ["Wed", "Fri", "Sun"] and time_str == "15:00":
            try:
                await bot.send_message(
                    chat_id=CHAT_ID,
                    text="🥦 Напоминание! Не забудь заполнить форму!",
                    parse_mode="Markdown",
                )
                print(f"✅ Расписание: уведомление отправлено {now}")
            except Exception as e:
                print("Ошибка при отправке по расписанию:", e)

        await asyncio.sleep(60)

# === Запуск Flask-приложения ===
if __name__ == "__main__":
    # Запускаем планировщик в фоне
    loop = asyncio.get_event_loop()
    loop.create_task(schedule_task())
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
