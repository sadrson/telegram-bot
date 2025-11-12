from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

import os

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

app = Flask(__name__)
bot = Bot(token=TOKEN)

# === Telegram Application ===
application = ApplicationBuilder().token(TOKEN).build()

# === Хэндлеры ===
async def start(update, context):
    await update.message.reply_text(f"✅ Бот работает! Твой chat_id: {update.effective_chat.id}")

async def echo(update, context):
    await update.message.reply_text(update.message.text)

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# === Webhook ===
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, bot)
    application.create_task(application.process_update(update))
    return "OK", 200

@app.route("/", methods=["GET"])
def home():
    return "Бот запущен 🚀", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
