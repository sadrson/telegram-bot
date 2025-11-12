import asyncio
from datetime import datetime
from flask import Flask, request, jsonify
import pytz
import requests
import threading
import time

# ===== Настройки =====
BOT_TOKEN = "ВАШ_BOT_TOKEN"
CHAT_ID = "ВАШ_CHAT_ID"
TIMEZONE = "Asia/Almaty"  # UTC+5
SCHEDULE_DAYS = ["Wed", "Fri", "Sun"]
SCHEDULE_TIME = "15:00"  # время в HH:MM

# Сообщение
TEXT = (
    "🥦 Напоминание! Не забудь заполнить "
    "[форму](https://docs.google.com/forms/d/e/1FAIpQLSeG38n-P76ju46Zi6D4CHX8t6zfbxN506NupZboNeERhkT81A/viewform)"
)

# ===== Flask =====
app = Flask(__name__)

@app.route("/", methods=["GET", "HEAD"])
def index():
    return "OK", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("Webhook received:", data)
    return jsonify({"ok": True})

# ===== Функция отправки уведомления =====
def send_telegram_message(text: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    resp = requests.post(url, data=data)
    if resp.status_code == 200:
        print("✅ Уведомление реально отправлено")
    else:
        print("❌ Ошибка отправки:", resp.text)

# ===== Scheduler =====
def scheduler():
    tz = pytz.timezone(TIMEZONE)
    while True:
        now = datetime.now(tz)
        weekday = now.strftime("%a")  # Mon, Tue, Wed ...
        time_str = now.strftime("%H:%M")
        if weekday in SCHEDULE_DAYS and time_str == SCHEDULE_TIME:
            send_telegram_message(TEXT)
            # Ждем 60 секунд, чтобы не отправилось несколько раз в одну минуту
            time.sleep(60)
        time.sleep(5)

# ===== Запуск scheduler в отдельном потоке =====
threading.Thread(target=scheduler, daemon=True).start()

# ===== Запуск Flask =====
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
