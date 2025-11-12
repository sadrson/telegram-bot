import os
import logging
from flask import Flask, request
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
TIMEZONE = "Asia/Almaty"  # UTC+5

# Расписание: Среда, Пятница, Воскресенье в 16:25
SCHEDULE_CONFIG = {
    'days': ['wed', 'fri', 'sun'],
    'hour': 16,
    'minute': 25
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

# ===== ПРОВЕРКА ПЕРЕМЕННЫХ ОКРУЖЕНИЯ =====
def validate_config():
    """Проверяет обязательные переменные окружения"""
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN не установлен")
    if not CHAT_ID:
        raise ValueError("CHAT_ID не установлен")
    
    try:
        chat_id_int = int(CHAT_ID)
    except ValueError:
        raise ValueError("CHAT_ID должен быть числовым значением")
    
    logger.info("Конфигурация проверена успешно")

# ===== ИНИЦИАЛИЗАЦИЯ =====
try:
    validate_config()
    bot = Bot(BOT_TOKEN)
    app = Flask(__name__)
except Exception as e:
    logger.error(f"Ошибка инициализации: {e}")
    raise

# ===== ФУНКЦИИ БОТА =====
def send_telegram_message(text, parse_mode='Markdown'):
    """Отправляет сообщение в Telegram с обработкой ошибок"""
    try:
        bot.send_message(
            chat_id=CHAT_ID,
            text=text,
            parse_mode=parse_mode,
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
    tz = pytz.timezone(TIMEZONE)
    current_time = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"Попытка отправки напоминания в {current_time}")
    
    success = send_telegram_message(MESSAGE_TEXTS['reminder'])
    
    if success:
        logger.info("Напоминание отправлено успешно")
    else:
        logger.error("Не удалось отправить напоминание")

def send_test_message():
    """Отправляет тестовое сообщение для проверки"""
    success = send_telegram_message(MESSAGE_TEXTS['test'])
    return success

# ===== ПЛАНИРОВЩИК =====
def setup_scheduler():
    """Настраивает и запускает планировщик задач"""
    jobstores = {
        'default': MemoryJobStore()
    }
    executors = {
        'default': ThreadPoolExecutor(5)
    }
    job_defaults = {
        'coalesce': True,  # Объединять повторные запуски
        'max_instances': 1,
        'misfire_grace_time': 300  # 5 минут grace period
    }
    
    scheduler = BackgroundScheduler(
        jobstores=jobstores,
        executors=executors,
        job_defaults=job_defaults,
        timezone=pytz.timezone(TIMEZONE)
    )
    
    # Добавляем основное задание
    scheduler.add_job(
        send_reminder,
        'cron',
        day_of_week=','.join(SCHEDULE_CONFIG['days']),  # ← ИСПРАВЛЕНО!
        hour=SCHEDULE_CONFIG['hour'],
        minute=SCHEDULE_CONFIG['minute'],
        id='weekly_reminder',
        name='Еженедельное напоминание о форме',
        replace_existing=True
    )
    
    # Тестовое задание (можно удалить в продакшене)
    scheduler.add_job(
        send_test_message,
        'cron',
        hour=12,
        minute=0,
        id='daily_test',
        name='Ежедневное тестовое сообщение'
    )
    
    scheduler.start()
    logger.info("Планировщик запущен")
    
    # Логируем расписание
    jobs = scheduler.get_jobs()
    for job in jobs:
        logger.info(f"Задание: {job.name} - Следующий запуск: {job.next_run_time}")
    
    return scheduler

# ===== WEB ROUTES =====
@app.route("/", methods=["GET"])
def index():
    """Главная страница - статус бота"""
    status_info = {
        "status": "active",
        "service": "Telegram Reminder Bot",
        "schedule": {
            "days": SCHEDULE_CONFIG['days'],
            "time": f"{SCHEDULE_CONFIG['hour']}:{SCHEDULE_CONFIG['minute']:02d}",
            "timezone": TIMEZONE
        },
        "next_reminder": get_next_reminder_time(),
        "timestamp": datetime.now(pytz.timezone(TIMEZONE)).isoformat()
    }
    
    return {
        "message": "🤖 Бот уведомлений активен",
        "data": status_info
    }, 200

@app.route("/health", methods=["GET"])
def health_check():
    """Health check для мониторинга"""
    try:
        # Проверяем соединение с Telegram
        bot.get_me()
        return {"status": "healthy", "telegram": "connected"}, 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}, 500

@app.route("/test", methods=["POST"])
def test_notification():
    """Ручка для тестирования уведомления"""
    success = send_test_message()
    
    if success:
        return {"message": "Тестовое сообщение отправлено"}, 200
    else:
        return {"error": "Не удалось отправить тестовое сообщение"}, 500

@app.route("/reminder", methods=["POST"])
def trigger_reminder():
    """Ручка для принудительной отправки напоминания"""
    success = send_telegram_message(MESSAGE_TEXTS['reminder'])
    
    if success:
        return {"message": "Напоминание отправлено"}, 200
    else:
        return {"error": "Не удалось отправить напоминание"}, 500

def get_next_reminder_time():
    """Возвращает время следующего напоминания"""
    from apscheduler.triggers.cron import CronTrigger
    
    # Объединяем дни в строку через запятую
    days_str = ','.join(SCHEDULE_CONFIG['days'])  # ← ИСПРАВЛЕНО!
    
    trigger = CronTrigger(
        day_of_week=days_str,  # 'wed,fri,sun'
        hour=SCHEDULE_CONFIG['hour'],
        minute=SCHEDULE_CONFIG['minute'],
        timezone=TIMEZONE
    )
    
    next_run = trigger.get_next_fire_time(None, datetime.now(pytz.timezone(TIMEZONE)))
    return next_run.isoformat() if next_run else None

# ===== ЗАПУСК ПРИЛОЖЕНИЯ =====
if __name__ == "__main__":
    try:
        # Запускаем планировщик
        scheduler = setup_scheduler()
        
        # Информация о запуске
        logger.info("=" * 50)
        logger.info("🤖 Telegram Reminder Bot запущен")
        logger.info(f"⏰ Расписание: {SCHEDULE_CONFIG['days']} в {SCHEDULE_CONFIG['hour']}:{SCHEDULE_CONFIG['minute']:02d}")
        logger.info(f"🌍 Часовой пояс: {TIMEZONE}")
        logger.info("=" * 50)
        
        # Запускаем Flask приложение
        port = int(os.environ.get("PORT", 10000))
        app.run(host="0.0.0.0", port=port, debug=False)
        
    except Exception as e:
        logger.error(f"Фатальная ошибка при запуске: {e}")
        if 'scheduler' in locals():
            scheduler.shutdown()
