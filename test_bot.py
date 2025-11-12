from flask import Flask
import asyncio
import datetime
import pytz
from telegram import Bot, ParseMode
import threading

BOT_TOKEN = "ВАШ_BOT_TOKEN"
CHAT_ID = "ВАШ_CHAT_ID"

bot = Bot(token=BOT_TOKEN)
app = Flask(__name__)

SCHEDULE_DAYS = ["Wed", "Fri", "Sun"]
HOUR, MINUTE = 15, 0  # Время уведомления (15:00 UTC+5)

async def send_reminder():
    text = (
        "🥦 Напоминание! Не забудь заполнить "
        "[форму](https://docs.google.com/forms/d/e/1FAIpQLSeG38n-P76ju46Zi6D4CHX8t6zfbxN506NupZboNeERhkT81A/viewform)"
    )
    await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode=ParseMode.MARKDOWN)
    print(f"✅ Уведомление отправлено: {datetime.datetime.now()}")

async def scheduler():
    tz = pytz.timezone("Asia/Almaty")  # UTC+5
    while True:
        now = datetime.datetime.now(tz)
        today_str = now.strftime("%a")

        send_time = tz.localize(datetime.datetime(now.year, now.month, now.day, HOUR, MINUTE))
        wait_seconds = (send_time - now).total_seconds()

        if today_str in SCHEDULE_DAYS and wait_seconds > 0:
            await asyncio.sleep(wait_seconds)
            await send_reminder()
        else:
            await asyncio.sleep(60)

# Запуск asyncio scheduler в отдельном потоке, чтобы Flask не блокировался
def start_scheduler():
    asyncio.run(scheduler())

threading.Thread(target=start_scheduler, daemon=True).start()

@app.route("/")
def index():
    return "Bot is running ✅"

@app.route("/webhook", methods=["POST"])
def webhook():
    # Заглушка для webhook, можно обработать входящие сообщения
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
