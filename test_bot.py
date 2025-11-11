from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import os
import asyncio
import threading
import datetime

# === Настройки ===
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")  # ID чата для уведомлений
WEBHOOK_URL = os.getenv("RENDER_EXTERNAL_HOSTNAME")  # если нужен вебхук, можно указать

app = Flask(__name__)

# === Telegram Application ===
application = Application.builder().token(TOKEN).build()

# === Асинхронный event loop в фоне ===
loop = asyncio.new_event_loop()
def start_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()
threading.Thread(target=start_loop, args=(loop,), daemon=True).start()

# === Команды ===
async def start(update: Update, context):
    chat_id = update.message.chat_id
    print(f"Chat ID: {chat_id}")  # вывод в лог для проверки
    await update.message.reply_text(f"✅ Бот успешно работает! Твой chat_id: {chat_id}")

application.add_handler(CommandHandler("start", start))

# Эхо-ответ на текстовые сообщения
async def echo(update: Update, context):
    await update.message.reply_text(update.message.text)

application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# === Webhook endpoint ===
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)

    async def process_update():
        if not application._initialized:
            await application.initialize()
        await application.process_update(update)

    asyncio.run(process_update())
    return jsonify({"ok": True}), 200

@app.route("/", methods=["GET"])
def home():
    return "Бот запущен 🚀", 200

# === Планировщик уведомлений ===
def scheduler():
    async def send_reminder():
        chat_id = CHAT_ID
        if not chat_id:
            print("❌ CHAT_ID не установлен!")
            return
        text = (
            "🥦 Напоминание! Не забудь заполнить "
            "[форму](https://docs.google.com/forms/d/e/1FAIpQLSeG38n-P76ju46Zi6D4CHX8t6zfbxN506NupZboNeERhkT81A/viewform)"
        )
        try:
            await application.bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")
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
                await asyncio.sleep(61)  # чтобы не сработало дважды
            await asyncio.sleep(30)

    asyncio.run_coroutine_threadsafe(job(), loop)

# Запуск планировщика
threading.Thread(target=scheduler, daemon=True).start()

# === Запуск Flask ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
