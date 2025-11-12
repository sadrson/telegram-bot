import os
from flask import Flask, request
from telegram import Bot
from datetime import datetime
import pytz

# Конфигурация
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
DAYS = ["Wed", "Fri", "Sun"]
HOUR = 15
MINUTE = 57
TIMEZONE = "Asia/Almaty"

# Инициализация
bot = Bot(BOT_TOKEN)
app = Flask(__name__)

def send_reminder():
    """Отправляет напоминание"""
    text = (
        "🥦 Напоминание! Не забудь заполнить "
        "[форму](https://docs.google.com/forms/d/e/1FAIpQLSeG38n-P76ju46Zi6D4CHX8t6zfbxN506NupZboNeERhkT81A/viewform)"
    )
    bot.send_message(chat_id=CHAT_ID, text=text, parse_mode="Markdown")

@app.route("/", methods=["GET", "HEAD"])
def index():
    return "Bot is running ✅", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        tz = pytz.timezone(TIMEZONE)
        now = datetime.now(tz)
        weekday = now.strftime("%a")

        # Проверяем условие с небольшим окном
        if (weekday in DAYS and 
            now.hour == HOUR and 
            now.minute == MINUTE and
            now.second < 10):
            
            send_reminder()
            return "Notification sent ✅", 200

        return "Webhook received", 200
        
    except Exception as e:
        print(f"Error in webhook: {e}")
        return "Error", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

