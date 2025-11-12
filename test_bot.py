import asyncio
import datetime
import pytz
from telegram import Bot, ParseMode

BOT_TOKEN = "ВАШ_BOT_TOKEN"
CHAT_ID = "ВАШ_CHAT_ID"

bot = Bot(token=BOT_TOKEN)

# Дни недели для уведомлений
SCHEDULE_DAYS = ["Wed", "Fri", "Sun"]  # Среда, Пятница, Воскресенье
HOUR, MINUTE = 15, 0  # Время уведомления (15:00 UTC+5)

async def send_reminder():
    text = (
        "🥦 Напоминание! Не забудь заполнить "
        "[форму](https://docs.google.com/forms/d/e/1FAIpQLSeG38n-P76ju46Zi6D4CHX8t6zfbxN506NupZboNeERhkT81A/viewform)"
    )
    await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode=ParseMode.MARKDOWN)
    print(f"✅ Уведомление отправлено: {datetime.datetime.now()}")

async def scheduler():
    tz = pytz.timezone("Asia/Almaty")  # UTC+5
    while True:
        now = datetime.datetime.now(tz)
        today_str = now.strftime("%a")  # 'Wed', 'Thu', etc.

        # Если сегодня день уведомления и время меньше HOUR:MINUTE
        send_time = tz.localize(datetime.datetime(now.year, now.month, now.day, HOUR, MINUTE))
        wait_seconds = (send_time - now).total_seconds()

        if today_str in SCHEDULE_DAYS and wait_seconds > 0:
            print(f"Ждем {int(wait_seconds)} секунд до отправки уведомления...")
            await asyncio.sleep(wait_seconds)
            await send_reminder()
        else:
            # Если день не тот или время уже прошло, ждем до следующей минуты
            await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(scheduler())
