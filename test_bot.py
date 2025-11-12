from flask import Flask, request
from telegram import Bot
import os
import datetime
import pytz
import asyncio

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

bot = Bot(token=BOT_TOKEN)

# сообщение с формой
TEXT = (
    "🥦 Напоминание! Не забудь заполнить "
    "[форму](https://docs.google.com/forms/d/e/1FAIpQLSeG38n-P76ju46Zi6D4CHX8t6zfbxN506NupZboNeERhkT81A/viewform)"
)

# UTC+5
TZ = pytz.timezone("Asia/Almaty")
SCHEDULE_DAYS = ["Wed", "Fri", "Sun"]
SCHEDULE_HOUR = 15
SCHEDULE_MINUTE = 0

async def send_message():
    await bot.send_message(chat_id=CHAT_ID, text=TEXT, parse_mode="Markdown")

@app.route("/send", methods=["POST"])
def send():
    now = datetime.datetime.now(TZ)
    day = now.strftime("%a")  # 'Wed', 'Fri', 'Sun'
    if day in SCHEDULE_DAYS and now.hour == SCHEDULE_HOUR and now.minute == SCHEDULE_MINUTE:
        asyncio.run(send_message())
        return "Notification sent ✅", 200
    return "Not scheduled time ⏰", 200

@app.route("/")
def index():
    return "Bot is running ✅"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
