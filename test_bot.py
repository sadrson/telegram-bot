import asyncio
from datetime import datetime, timedelta
from telegram import Bot

# =======================
# Настройки бота
# =======================
BOT_TOKEN = "ВАШ_BOT_TOKEN"
CHAT_ID = "ВАШ_CHAT_ID"
bot = Bot(token=BOT_TOKEN)

# Сообщение с формой
text = (
    "🥦 Напоминание! Не забудь заполнить "
    "[форму](https://docs.google.com/forms/d/e/1FAIpQLSeG38n-P76ju46Zi6D4CHX8t6zfbxN506NupZboNeERhkT81A/viewform)"
)

# Дни недели для уведомлений
DAYS = ["Wed", "Fri", "Sun"]
TIME_STR = "15:00"  # время UTC+5


# =======================
# Функция отправки уведомления
# =======================
async def send_reminder():
    try:
        await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode="Markdown")
        print(f"✅ Уведомление отправлено {datetime.now()}")
    except Exception as e:
        print(f"❌ Ошибка отправки уведомления: {e}")


# =======================
# Основной цикл
# =======================
async def scheduler():
    while True:
        # Текущее время UTC+5
        now_utc = datetime.utcnow()
        now = now_utc + timedelta(hours=5)

        current_day = now.strftime("%a")  # 'Mon', 'Tue', 'Wed', ...
        current_time = now.strftime("%H:%M")

        # Проверяем день и время
        if current_day in DAYS and current_time == TIME_STR:
            await send_reminder()
            await asyncio.sleep(60)  # ждём минуту, чтобы не отправлять повторно

        await asyncio.sleep(10)  # проверяем каждые 10 секунд


# =======================
# Запуск
# =======================
if __name__ == "__main__":
    asyncio.run(scheduler())
