from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import os
import asyncio
import threading

# === Настройки ===
TOKEN = os.getenv("BOT_TOKEN")            # токен бота
CHAT_ID = os.getenv("CHAT_ID")            # ID чата (для уведомлений, если нужно)
WEBHOOK_PATH = "/webhook"                 # путь webhook
WEBHOOK_URL = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}{WEBHOOK_PATH}"

app = Flask(__name__)

# === Создаем Telegram Application ===
application = Application.builder().token(TOKEN).build()

# === Асинхронный loop в фоне ===
loop = asyncio.new_event_loop()
def start_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()
threading.Thread(target=start_loop, args=(loop,), daemon=True).start()

# === Команды ===
async def start(update: Update, context):
    chat_id = update.effective_chat.id
    print(f"Chat ID: {chat_id}")  # выводим для логов Render
    await update.message.reply_text(f"✅ Бот работает! Твой chat_id: {chat_id}")

async def echo(update: Update, context):
    await update.message.reply_text(update.message.text)

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# === Webhook endpoint ===
@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    # Отправляем на обработку в Telegram Application через event loop
    asyncio.run_coroutine_threadsafe(application.process_update(update), loop)
    return jsonify({"ok": True})

@app.route("/", methods=["GET"])
def home():
    return "Бот запущен 🚀"

# === Запуск Flask ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    # Устанавливаем webhook при старте (один раз)
    import requests
    r = requests.get(f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={WEBHOOK_URL}")
    print(r.json())
    
    app.run(host="0.0.0.0", port=port)
