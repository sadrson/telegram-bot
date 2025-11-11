from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import os
import asyncio
import threading

TOKEN = os.getenv("BOT_TOKEN")
app = Flask(__name__)

application = Application.builder().token(TOKEN).build()

# глобальные переменные
loop = None
loop_thread = None

def ensure_loop_running():
    global loop, loop_thread
    if loop is None or not loop.is_running():
        loop = asyncio.new_event_loop()

        def run_loop():
            asyncio.set_event_loop(loop)
            loop.run_forever()

        loop_thread = threading.Thread(target=run_loop, daemon=True)
        loop_thread.start()

ensure_loop_running()

async def start(update: Update, context):
    await update.message.reply_text("✅ Бот успешно работает на Render!")

async def echo(update: Update, context):
    await update.message.reply_text(update.message.text)

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        ensure_loop_running()
        data = request.get_json(force=True)
        update = Update.de_json(data, application.bot)

        async def process_update():
            if not application._initialized:
                await application.initialize()
            await application.process_update(update)

        asyncio.run_coroutine_threadsafe(process_update(), loop)

    except Exception as e:
        print(f"Webhook error: {e}")

    return jsonify({"ok": True})

@app.route("/")
def home():
    return "Бот запущен 🚀", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
