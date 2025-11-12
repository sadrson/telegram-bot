from flask import Flask, request, jsonify
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import os
import asyncio
import threading
import datetime

# === Настройки ===
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")  # для уведомлений
WEBHOOK_URL = f"https://telegram-bot-vluf.onrender.com/webhook"

app = Flask(__name__)

# === Telegram Application ===
application = Application.builder().token(TOKEN).build()

# === Автоматическая установка вебхука ===
bot = Bot(token=TOKEN)
bot.delete_webhook()
print("Старый вебхук удалён")
success = bot.set_webhook(url=WEBHOOK_URL)
if success:
    print(f"✅ Вебхук успешно установлен: {WEBHOOK_URL}")
else:
    print("❌ Ошибка установки вебхука")

# === Асинхронный event loop в фоне ===
loop = asyncio.new_event_loop()
def start_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()
threading.Thread(target=start_loop, args=(loop,), daemon=True).start()

# === Команды ===
async def start(update: Update, context):
    chat_id = update.effective_chat.id
    print(f"Chat ID: {chat_id}")
    await update.message.reply_text(f"✅ Бот успешно работает! Твой chat_id: {chat_id}")

application.add_handler(CommandHandler("start", start))

# Эхо для всех текстовых сообщений
async def echo(update: Update, context):
    await update.message.reply_text(update.message.text)

application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# === Webhook endpoint ===
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    asyncio.run_coroutine_threadsafe(application.process_update(update), loop)
    return jsonify({"ok": True}), 200

@app.route("/", methods=["GET"])
def home():
    return "Бот запущен 🚀", 200

# === Планировщик уведомлений ===
def scheduler():
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

    async def job():
        while True:
            now = datetime.datetime.utcnow() + datetime.timedelta(hours=5)  # UTC+5
            day = now.strftime("%a")  # Wed, Fri, Sun
            time_str = now.strftime("%H:%M")
            if day in ["Wed", "Fri", "Sun"] and time_str == "15:00":
                await send_reminder()
                await asyncio.sleep(61)
            await asyncio.sleep(30)

    asyncio.run_coroutine_threadsafe(job(), loop)

threading.Thread(target=scheduler, daemon=True).start()

# === Запуск Flask ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
