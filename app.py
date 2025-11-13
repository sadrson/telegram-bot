import os
import logging
from flask import Flask
import requests
import pytz
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

# ===== КОНФИГУРАЦИЯ =====
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID") 
TIMEZONE = "Asia/Bishkek"  # UTC+6

# Расписание: Каждый день в 08:00
SCHEDULE_CONFIG = {
    'days': ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'],  # ВСЕ ДНИ
    'hour': 8,  # 08:00
    'minute': 0
}

MESSAGE_TEXTS = {
    'reminder': "🍕 Напоминание! Не забудь заполнить [форму](https://docs.google.com/forms/d/e/1FAIpQLSeG38n-P76ju46Zi6D4CHX8t6zfbxN506NupZboNeERhkT81A/viewform).",
    'test': "✅ Тестовое сообщение! Бот работает корректно."
}

# ===== НАСТРОЙКА ЛОГИРОВАНИЯ =====
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def send_telegram_message(text):
    """Отправляет сообщение в Telegram через HTTP API (как в Replit)"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": CHAT_ID, 
            "text": text, 
            "parse_mode": "Markdown"
        }
        
        response = requests.post(url, data=data)
        if response.ok:
            logger.info("✅ Сообщение успешно отправлено!")
            return True
        else:
            logger.error(f"⚠️ Ошибка при отправке: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        return False

def send_reminder():
    """Отправляет основное напоминание"""
    current_time = datetime.now(pytz.timezone(TIMEZONE)).strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"🕐 Отправка напоминания в {current_time}")
    return send_telegram_message(MESSAGE_TEXTS['reminder'])

def send_test_message():
    """Отправляет тестовое сообщение"""
    logger.info("🧪 Отправка тестового сообщения")
    return send_telegram_message(MESSAGE_TEXTS['test'])

def setup_scheduler():
    """Настраивает планировщик"""
    scheduler = BackgroundScheduler(timezone=pytz.timezone(TIMEZONE))
    
    # Основное расписание - КАЖДЫЙ ДЕНЬ в 08:00
    scheduler.add_job(
        send_reminder,
        'cron',
        day_of_week=','.join(SCHEDULE_CONFIG['days']),
        hour=SCHEDULE_CONFIG['hour'],
        minute=SCHEDULE_CONFIG['minute'],
        id='daily_reminder'
    )
    
    scheduler.start()
    logger.info(f"🤖 Планировщик запущен: КАЖДЫЙ ДЕНЬ в {SCHEDULE_CONFIG['hour']:02d}:{SCHEDULE_CONFIG['minute']:02d}")
    
    # Логируем следующее выполнение
    jobs = scheduler.get_jobs()
    for job in jobs:
        logger.info(f"🎯 Следующий запуск: {job.next_run_time}")
    
    return scheduler

@app.route("/")
def home():
    return "🤖 Бот уведомлений активен"

@app.route("/test", methods=["POST"])
def test_notification():
    success = send_test_message()
    return {"message": "Тест отправлен"}, 200 if success else 500

@app.route("/reminder", methods=["POST"])
def trigger_reminder():
    success = send_reminder()
    return {"message": "Напоминание отправлено"}, 200 if success else 500

@app.route("/ping")
def ping():
    return "pong", 200

if __name__ == "__main__":
    # Запускаем планировщик
    scheduler = setup_scheduler()
    
    # Запускаем Flask
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"🚀 Бот запущен на порту {port}")
    app.run(host="0.0.0.0", port=port)
