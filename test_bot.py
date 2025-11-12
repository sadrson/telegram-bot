import os
import threading
import datetime
import pytz
import time
from flask import Flask, request
from telegram import Bot
from telegram.constants import ParseMode  # ✅ исправлено место импорта

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=BOT_TOKEN)

def send_reminder():
    text = (
        "🥦 Напоминание! Не забудь заполнить "
        "[форму](https://docs.google.com/forms/d/e/1FAIpQLSeG38n-P76ju46Zi6D4CHX8t6zfbxN506NupZboNeERhkT81A/viewform)"
    )
    try:
        bot.send_message(chat_id=CHAT_ID, text=text, parse_mode=ParseMode.MARKDOWN)
        print(f"✅ Сообщение отправлено {datetime.datetime.now()}")
    except Exception as e:
        print(f"Ошибка отправки: {e}")

def scheduler():
    tz = pytz.timezone("Asia/Yekaterinburg")  # UTC+5
    days = ["Wed", "Fri", "Sun"]

    while True:
        now = datetime.datetime.now(tz)
        weekday = now.strftime("%a")
        time_str = now.strftime("%H:%M")

        if weekday in days and time_str == "15:00":
            send_reminder()
            time.sleep(60)  # чтобы не отправлял повторно в ту же минуту

        time.sleep(20)  # проверка каждые 20 секунд

@app.route("/")
def home():
    return "Бот работает!"

@app.route("/webhook", methods=["POST"])
def webhook():
    return {"ok": True}

if __name__ == "__main__":
    thread = threading.Thread(target=scheduler, daemon=True)
    thread.start()
    app.run(host="0.0.0.0", port=10000)
