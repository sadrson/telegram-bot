import os
import logging
from flask import Flask
from telegram import Bot
from telegram.error import TelegramError
from apscheduler.schedulers.background import BackgroundScheduler
import pytz
from datetime import datetime

# ===== КОНФИГУРАЦИЯ =====
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
TIMEZONE = "Asia/Bishkek"  # UTC+6

# Расписание: Среда, Пятница, Воскресенье в 16:45
SCHEDULE_CONFIG = {
    'days': ['wed', 'fri', 'sun'],
    'hour': 16,
    'minute': 45  # ← ИЗМЕНИЛ НА 45 ДЛЯ ТЕСТА
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
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ===== ИНИЦИАЛИЗАЦИЯ =====
try:
    bot = Bot(BOT_TOKEN)
    app = Flask(__name__)
except Exception as e:
    logger.error(f"Ошибка инициализации: {e}")
    raise

def send_telegram_message(text):
    try:
        bot.send_message(
            chat_id=CHAT_ID, 
            text=text, 
            parse_mode='Markdown',
            disable_web_page_preview=False
        )
        logger.info("Сообщение успешно отправлено")
        return True
    except TelegramError as e:
        logger.error(f"Ошибка Telegram: {e}")
        return False
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")
        return False

def send_reminder():
    """Отправляет основное напоминание"""
    current_time = datetime.now(pytz.timezone(TIMEZONE)).strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"🕐 Попытка отправки напоминания в {current_time}")
    
    success = send_telegram_message(MESSAGE_TEXTS['reminder'])
    
    if success:
        logger.info("✅ Напоминание отправлено успешно")
    else:
        logger.error("❌ Не удалось отправить напоминание")

def send_test_message():
    return send_telegram_message(MESSAGE_TEXTS['test'])

def setup_scheduler():
    """Настраивает и запускает планировщик задач"""
    scheduler = BackgroundScheduler(timezone=pytz.timezone(TIMEZONE))
    
    scheduler.add_job(
        send_reminder,
        'cron',
        day_of_week=','.join(SCHEDULE_CONFIG['days']),
        hour=SCHEDULE_CONFIG['hour'],
        minute=SCHEDULE_CONFIG['minute'],
        id='weekly_reminder',
        name='Еженедельное напоминание'
    )
    
    scheduler.start()
    
    # Логируем запуск
    logger.info("=" * 50)
    logger.info("🤖 Планировщик запущен!")
    logger.info(f"⏰ Расписание: {SCHEDULE_CONFIG['days']} в {SCHEDULE_CONFIG['hour']}:{SCHEDULE_CONFIG['minute']:02d}")
    logger.info(f"🌍 Часовой пояс: {TIMEZONE}")
    
    # Логируем следующее выполнение
    jobs = scheduler.get_jobs()
    for job in jobs:
        logger.info(f"📅 Задание: {job.name}")
        logger.info(f"🔄 Следующий запуск: {job.next_run_time}")
    logger.info("=" * 50)
    
    return scheduler

@app.route("/")
def index():
    return {
        "message": "🤖 Бот уведомлений активен",
        "data": {
            "status": "active",
            "service": "Telegram Reminder Bot",
            "schedule": {
                "days": SCHEDULE_CONFIG['days'],
                "time": f"{SCHEDULE_CONFIG['hour']}:{SCHEDULE_CONFIG['minute']:02d}",
                "timezone": TIMEZONE
            },
            "timestamp": datetime.now(pytz.timezone(TIMEZONE)).isoformat()
        }
    }, 200

@app.route("/test", methods=["POST"])
def test_notification():
    success = send_test_message()
    if success:
        return {"message": "Тестовое сообщение отправлено"}, 200
    else:
        return {"error": "Не удалось отправить тестовое сообщение"}, 500

# Добавим эндпоинт для принудительной отправки
@app.route("/reminder", methods=["POST"])
def trigger_reminder():
    """Ручка для принудительной отправки напоминания"""
    success = send_telegram_message(MESSAGE_TEXTS['reminder'])
    if success:
        return {"message": "Напоминание отправлено"}, 200
    else:
        return {"error": "Не удалось отправить напоминание"}, 500

if __name__ == "__main__":
    try:
        scheduler = setup_scheduler()
        port = int(os.environ.get("PORT", 10000))
        app.run(host="0.0.0.0", port=port, debug=False)
    except Exception as e:
        logger.error(f"Фатальная ошибка при запуске: {e}")
        if 'scheduler' in locals():
            scheduler.shutdown()
