import os
import logging
from flask import Flask
from telegram import Bot
from telegram.error import TelegramError
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
import pytz
from datetime import datetime

# ===== КОНФИГУРАЦИЯ =====
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
TIMEZONE = "Asia/Bishkek"  # UTC+6 - ИСПРАВЛЕНО!

# Расписание: Среда, Пятница, Воскресенье в 16:35
SCHEDULE_CONFIG = {
    'days': ['wed', 'fri', 'sun'],
    'hour': 16,
    'minute': 35
}

MESSAGE_TEXTS = {
    'reminder': (
        "🥦 **Напоминание!**\n\n"
        "Не забудь заполнить форму питания:\n"
        "[📝 Форма для заполнения](https://docs.google.com/forms/d/e/1FAIpQLSeG38n-P76ju46Zi6D4CHX8t6zfbxN506NupZboNeERhkT81A/viewform)\n\n"
        "_Спасибо! 🙏_"
    ),
    'test': "✅ Тестовое сообщение! Бот работает корректно."
}

# ===== НАСТРОЙКА ЛОГИРОВАНИЯ =====
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== ИНИЦИАЛИЗАЦИЯ =====
bot = Bot(BOT_TOKEN)
app = Flask(__name__)

def send_telegram_message(text):
    try:
        bot.send_message(chat_id=CHAT_ID, text=text, parse_mode='Markdown')
        return True
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return False

def send_reminder():
    current_time = datetime.now(pytz.timezone(TIMEZONE)).strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"Отправка напоминания в {current_time}")
    send_telegram_message(MESSAGE_TEXTS['reminder'])

def send_test_message():
    return send_telegram_message(MESSAGE_TEXTS['test'])

def setup_scheduler():
    scheduler = BackgroundScheduler(timezone=pytz.timezone(TIMEZONE))
    
    scheduler.add_job(
        send_reminder,
        'cron',
        day_of_week=','.join(SCHEDULE_CONFIG['days']),
        hour=SCHEDULE_CONFIG['hour'],
        minute=SCHEDULE_CONFIG['minute'],
        id='weekly_reminder'
    )
    
    scheduler.start()
    return scheduler

@app.route("/")
def index():
    return {
        "message": "🤖 Бот уведомлений активен",
        "data": {
            "status": "active",
            "timezone": TIMEZONE,
            "timestamp": datetime.now(pytz.timezone(TIMEZONE)).isoformat()
        }
    }, 200

@app.route("/test", methods=["POST"])
def test_notification():
    success = send_test_message()
    return {"message": "Тест отправлен"}, 200 if success else 500

if __name__ == "__main__":
    scheduler = setup_scheduler()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
