from flask import Flask
from telegram import Bot
import os
from datetime import datetime
import pytz

app = Flask(__name__)

BOT_TOKEN = os.environ['BOT_TOKEN']
CHAT_ID = os.environ['CHAT_ID']
bot = Bot(token=BOT_TOKEN)

# Дни для уведомлений
NOTIFY_DAYS = ["Wed", "Fri", "Sun"]
# Время для уведомления в формате "HH:MM"
NOTIFY_TIME = "15:35"
# Часовой пояс
TZ = pytz.timezone("Asia/Almaty")  # UTC+5

@app.route("/send")
def send():
    now = datetime.now(TZ)
    day_str = now.strftime("%a")  # Например "Wed"
    time_str = now.strftime("%H:%M")

    if day_str in NOTIFY_DAYS and time_str == NOTIFY_TIME:
        text = (
            "🥦 Напоминание! Не забудь заполнить "
            "[форму](https://docs.google.com/forms/d/e/1FAIpQLSeG38n-P76ju46Zi6D4CHX8t6zfbxN506NupZboNeERhkT81A/viewform)"
        )
        bot.send_message(chat_id=CHAT_ID, text=text, parse_mode="Markdown")
        return "✅ Уведомление отправлено!"
    return f"Сегодня {day_str}, текущее время {time_str}. Уведомление не отправлено."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
