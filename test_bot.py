import asyncio
from datetime import datetime
import pytz
from flask import Flask, request, jsonify
from telegram import Bot, ParseMode
from apscheduler.schedulers.background import BackgroundScheduler

# Настройки
BOT_TOKEN = "ВАШ_BOT_TOKEN"
CHAT_ID = "ВАШ_CHAT_ID"  # Личный chat_id
TIMEZONE = pytz.timezone("Asia/Almaty")  # UTC+5
DAYS = ["Wed", "Fri", "Sun"]  # дни недели
TIME_STR = "15:00"  # время уведомления

bot = Bot(token=BOT_TOKEN)

app = Flask(__name__)

# Функция отправки уведомления
async def send_reminder():
    text = (
        "🥦 Напоминание! Не забудь заполнить "
        "[форму](https://docs.google.com/forms/d/e/1FAIpQLSeG38n-P76ju46Zi6D4CHX8t6zfbxN506NupZboNeERhkT81A/viewform)"
    )
    try:
        await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode=ParseMode.MARKDOWN)
        print(f"✅ Уведомление отправлено {datetime.now()}")
    except Exception as e:
        print(f"❌ Ошибка отправки уведомления: {e}")

# Проверка времени и запуск уведомления
def scheduled_job():
    now = datetime.now(TIMEZONE)
    weekday = now.strftime("%a")  # e.g., 'Wed'
    time_str = now.strftime("%H:%M")
    if weekday in DAYS and time_str == TIME_STR:
        asyncio.run(send_reminder())

# Настройка планировщика
scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_job, "cron", minute="*")  # проверяем каждую минуту
scheduler.start()

# Вебхук для Telegram
@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json(force=True)
    print("Webhook received:", update)

    # Можно обрабатывать команды, например /start
    if "message" in update and "text" in update["message"]:
        text = update["message"]["text"]
        chat_id = update["message"]["chat"]["id"]
        if text == "/start":
            asyncio.run(bot.send_message(chat_id=chat_id, text="Бот работает ✅"))
    return jsonify({"ok": True})

# Главная страница (для проверки)
@app.route("/", methods=["GET", "HEAD"])
def index():
    return "Bot is running ✅", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
