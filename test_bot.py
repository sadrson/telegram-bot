import os
from flask import Flask, request
from telegram import Bot
from datetime import datetime
import pytz

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
bot = Bot(BOT_TOKEN)

app = Flask(__name__)

# Расписание уведомлений
DAYS = ["Wed", "Fri", "Sun"]
HOUR = 15
MINUTE = 48
TIMEZONE = "Asia/Almaty"  # UTC+5

@app.route("/", methods=["GET", "HEAD"])
def index():
    return "Bot is running ✅", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    # проверяем время и день
    tz = pytz.timezone(TIMEZONE)
    now = datetime.now(tz)
    weekday = now.strftime("%a")  # 'Wed', 'Fri', 'Sun' и т.д.

    if weekday in DAYS and now.hour == HOUR and now.minute == MINUTE:
        text = (
            "🥦 Напоминание! Не забудь заполнить "
            "[форму](https://docs.google.com/forms/d/e/1FAIpQLSeG38n-P76ju46Zi6D4CHX8t6zfbxN506NupZboNeERhkT81A/viewform)"
        )
        bot.send_message(chat_id=CHAT_ID, text=text, parse_mode="Markdown")
        return "Notification sent ✅", 200

    return "Webhook received", 200

if __name__ == "__main__":
