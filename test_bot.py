from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import os
import asyncio
import datetime

# ================= Настройки =================
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")  # куда отправлять уведомления
TIMEZONE_OFFSET = 5  # UTC+5
REMINDER_DAYS = ["Wed", "Fri", "Sun"]
REMINDER_TIME = "15:00"  # формат HH:MM

# ================= Flask =================
app = Flask(__name__)

# ================= Telegram =================
application = Application.builder().token(TOKEN).build()

# ---------------- Команды ----------------
async def start(update: Update, context):
    chat_id = update.message.chat_id
    print(f"Chat ID: {chat_id}")
    await update.message.reply_text(
        f"✅ Бот работает! Твой chat_id: {chat_id}"
    )

async def echo(update: Update, context):
    await update.message.reply_text(update.message.text)

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# ================= Webhook =================
@app.route("/webhook", methods=["POST"])
async def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return jsonify({"ok": True})

@app.route("/", methods=["GET"])
def home():
    return "Бот запущен 🚀", 200

# ================= Планировщик =================
async def send_reminder():
    if not CHAT_ID:
        print("❌ CHAT_ID не установлен!")
        return
    text = (
        "🥦 Напоминание! Не забудь заполнить "
        "[форму](https://docs.google.com/forms/d/e/1FAIpQLSeG38n-P76ju46Zi6D4CHX8t6zfbxN506NupZboNeERhkT81A/viewform)"
    )
    try:
        await application.bot.send_message(chat_id=CHAT_ID, text=text, parse_mode="Markdown")
        print(f"✅ Уведомление отправлено {datetime.datetime.now()}")
    except Exception as e:
        print(f"Ошибка отправки уведомления: {e}")

async def scheduler():
    while True:
        now = datetime.datetime.utcnow() + datetime.timedelta(hours=TIMEZONE_OFFSET)
        day = now.strftime("%a")
        time_str = now.strftime("%H:%M")
        if day in REMINDER_DAYS and time_str == REMINDER_TIME:
            await send_reminder()
            await asyncio.sleep(61)  # чтобы не сработало дважды
        await asyncio.sleep(30)

# ================= Запуск =================
async def main():
    # Запускаем планировщик
    asyncio.create_task(scheduler())
    # Запускаем Flask
    from hypercorn.asyncio import serve
    from hypercorn.config import Config

    config = Config()
    config.bind = ["0.0.0.0:10000"]  # порт
    await serve(app, config)

if __name__ == "__main__":
    asyncio.run(main())
