from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import os
import asyncio

TOKEN = os.getenv("BOT_TOKEN")
app = Flask(__name__)

application = Application.builder().token(TOKEN).build()

async def start(update: Update, context):
    await update.message.reply_text("✅ Бот успешно работает на Render!")

async def echo(update: Update, context):
    await update.message.reply_text(update.message.text)

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    loop = asyncio.get_event_loop()
    if not application._initialized:
        loop.run_until_complete(application.initialize())
    loop.create_task(application.process_update(update))
    return "ok", 200

@app.route("/", methods=["GET"])
def home():
    return "Бот запущен 🚀", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
