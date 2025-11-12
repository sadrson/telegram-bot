import os
import logging
from flask import Flask
from telegram import Bot
from telegram.error import TelegramError
from apscheduler.schedulers.background import BackgroundScheduler
import pytz
from datetime import datetime, timedelta

# ===== КОНФИГУРАЦИЯ =====
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
TIMEZONE = "Asia/Bishkek"  # UTC+6

# Расписание: Среда, Пятница, Воскресенье в 17:02
SCHEDULE_CONFIG = {
    'days': ['wed', 'fri', 'sun'],
    'hour': 17,
    'minute': 2
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
    logger.info("✅ Бот и Flask инициализированы")
except Exception as e:
    logger.error(f"❌ Ошибка инициализации: {e}")
    raise

def send_telegram_message(text):
    """Отправляет сообщение в Telegram"""
    try:
        bot.send_message(
            chat_id=CHAT_ID, 
            text=text, 
            parse_mode='Markdown',
            disable_web_page_preview=False
        )
        logger.info("✅ Сообщение успешно отправлено в Telegram")
        return True
    except TelegramError as e:
        logger.error(f"❌ Ошибка Telegram: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Неожиданная ошибка: {e}")
        return False

def send_reminder():
    """Отправляет основное напоминание"""
    current_time = datetime.now(pytz.timezone(TIMEZONE)).strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"🕐 ЗАПУСК: Отправка напоминания в {current_time}")
    
    success = send_telegram_message(MESSAGE_TEXTS['reminder'])
    
    if success:
        logger.info("🎉 Напоминание отправлено успешно!")
    else:
        logger.error("💥 Не удалось отправить напоминание")

def send_test_message():
    """Отправляет тестовое сообщение"""
    logger.info("🧪 Отправка тестового сообщения")
    return send_telegram_message(MESSAGE_TEXTS['test'])

# ===== ПЛАНИРОВЩИК =====
scheduler = None

def init_scheduler():
    """Инициализирует планировщик (только в главном процессе)"""
    global scheduler
    
    # Проверяем что мы в главном процессе Gunicorn
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        return
    if os.environ.get('GUNICORN_WORKER_ID') is not None:
        return
        
    logger.info("🔄 Инициализация планировщика в главном процессе...")
    
    scheduler = BackgroundScheduler(timezone=pytz.timezone(TIMEZONE))
    
    # ОСНОВНОЕ задание по расписанию
    scheduler.add_job(
        send_reminder,
        'cron',
        day_of_week=','.join(SCHEDULE_CONFIG['days']),
        hour=SCHEDULE_CONFIG['hour'],
        minute=SCHEDULE_CONFIG['minute'],
        id='weekly_reminder',
        name='Основное уведомление'
    )
    
    # ТЕСТОВОЕ задание - сработает через 1 минуту после запуска
    test_time = datetime.now(pytz.timezone(TIMEZONE)) + timedelta(minutes=1)
    scheduler.add_job(
        send_reminder,
        'date',
        run_date=test_time,
        id='test_job_1min',
        name='Тестовое уведомление через 1 минуту'
    )
    
    scheduler.start()
    
    # Детальное логирование
    logger.info("=" * 60)
    logger.info("🤖 ПЛАНИРОВЩИК УСПЕШНО ЗАПУЩЕН!")
    logger.info(f"🌍 Часовой пояс: {TIMEZONE}")
    logger.info(f"⏰ Основное расписание: {SCHEDULE_CONFIG['days']} в {SCHEDULE_CONFIG['hour']}:{SCHEDULE_CONFIG['minute']:02d}")
    
    jobs = scheduler.get_jobs()
    logger.info(f"📊 Всего активных задач: {len(jobs)}")
    
    for job in jobs:
        logger.info(f"🎯 Задача: {job.name}")
        logger.info(f"   Следующий запуск: {job.next_run_time}")
    
    logger.info("=" * 60)

# Инициализируем планировщик при импорте
init_scheduler()

# ===== WEB ROUTES =====
@app.route("/")
def index():
    """Главная страница - статус бота"""
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
    """Ручка для тестирования уведомления"""
    success = send_test_message()
    if success:
        return {"message": "✅ Тестовое сообщение отправлено"}, 200
    else:
        return {"error": "❌ Не удалось отправить тестовое сообщение"}, 500

@app.route("/reminder", methods=["POST"])
def trigger_reminder():
    """Ручка для принудительной отправки напоминания"""
    success = send_telegram_message(MESSAGE_TEXTS['reminder'])
    if success:
        return {"message": "✅ Напоминание отправлено"}, 200
    else:
        return {"error": "❌ Не удалось отправить напоминание"}, 500

@app.route("/ping")
def ping():
    """Простой пинг для мониторинга"""
    return "pong", 200

if __name__ == "__main__":
    # Для локального запуска
    init_scheduler()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
