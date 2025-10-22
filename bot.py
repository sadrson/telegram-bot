import telegram
import schedule
import asyncio
import time

# === 🔐 Токен твоего бота ===
TOKEN = "8274488039:AAEBT6A-NSFMINjrM1ZboPg8Iq7Eh-K-XK0"

# === 💬 Chat ID (кому бот отправляет сообщение) ===
CHAT_ID = 5364731536  # замени при необходимости на ID группы

# === 📨 Текст уведомления с кликабельной ссылкой ===
# используем HTML-разметку, чтобы избежать ошибок Markdown
MESSAGE_TEXT = (
    'Прошу заполнить <a href="https://docs.google.com/forms/d/e/1FAIpQLSeG38n-P76ju46Zi6D4CHX8t6zfbxN506NupZboNeERhkT81A/viewform">'
    'форму</a>, заявка принимается до 18:00'
)

# Создаём экземпляр бота
bot = telegram.Bot(token=TOKEN)

# === Асинхронная функция для отправки сообщений ===
async def send_message():
    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            text=MESSAGE_TEXT,
            parse_mode="HTML"  # используем HTML, чтобы избежать ошибок с Markdown
        )
        print("✅ Сообщение успешно отправлено!")
    except Exception as e:
        print(f"⚠️ Ошибка при отправке: {e}")

# === Планировщик задач ===
def run_scheduler():
    # Отправка в 15:00 в среду, пятницу и воскресенье
    schedule.every().wednesday.at("15:00").do(lambda: asyncio.run(send_message()))
    schedule.every().friday.at("15:00").do(lambda: asyncio.run(send_message()))
    schedule.every().sunday.at("15:00").do(lambda: asyncio.run(send_message()))

    # Тестовое сообщение при запуске
    print("🚀 Бот запущен, отправляю тестовое сообщение...")
    asyncio.run(send_message())

    print("🤖 Бот ждёт времени для следующих уведомлений...")

    # Бесконечный цикл проверки расписания
    while True:
        schedule.run_pending()
        time.sleep(1)

# === Точка входа ===
if __name__ == "__main__":
    run_scheduler()
