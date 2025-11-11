from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler
import os
import asyncio
import threading
import requests
import datetime

# === Настройки ===
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")  # ID чата для уведомлений
WEBHOOK_URL = "https://telegram-bot-vluf.onrender.com/webhook"

app = Flask(__name__)

# === Telegram Application ===
application = Application.builder().token(TOKEN).build()

# === Асинхронный event loop в фоне ===
loop = asyncio.new_event_loop()
def start_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

threading.Thread(target=start_loop, args=(loop,)).start()  # без daemon=True

# === Команды ===
async def start(update: Update, context):
    await update.message.reply_text(
        "✅ Бот запущен и будет присылать уведомления по расписанию."
    )

application.add_handler(CommandHandler("start", start))

# === Webhook endpoint ===
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)

    async def process():
        if not application._initialized:
            await application.initialize()
        await application.process_update(update)

    asyncio.run_coroutine_threadsafe(process(), loop)
    return jsonify({"ok": True})

@app.route("/", methods=["GET"])
def home():
    return "Бот запущен 🚀", 200

# === Планировщик уведомлений ===
def scheduler():
    async def send_reminder():
        text = (
            "🥦 Напоминание! Не забудь заполнить "
            "[форму](https://docs.google.com/forms/d/e/1FAIpQLSeG38n-P76ju46Zi6D4CHX8t6zfbxN506NupZboNeERhkT81A/viewform)"
        )
        try:
            await application.bot.send_message(
                chat_id=CHAT_ID, text=text, parse_mode="Markdown"
            )
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
                await asyncio.sleep(61)  # чтобы не сработало повторно в ту же минуту
            await asyncio.sleep(30)

    asyncio.run_coroutine_threadsafe(job(), loop)

# Запуск планировщика без daemon=True
threading.Thread(target=scheduler).start()

# === Установка вебхука ===
def set_webhook():
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
        resp = requests.post(url, data={"url": WEBHOOK_URL})
        if resp.status_code == 200 and resp.json().get("ok"):
            print(f"✅ Webhook установлен: {WEBHOOK_URL}")
        else:
            print(f"⚠️ Ошибка при установке вебхука: {resp.text}")
    except Exception as e:
        print(f"Webhook setup failed: {e}")

set_webhook()

# === Запуск Flask ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
