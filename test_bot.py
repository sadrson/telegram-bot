from flask import Flask, request
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler

app = Flask(__name__)

# Создаём бота
TOKEN = "<YOUR_BOT_TOKEN>"
application = ApplicationBuilder().token(TOKEN).build()

# Простейший хэндлер
async def start(update: Update, context):
    await update.message.reply_text("Бот работает 🚀")

application.add_handler(CommandHandler("start", start))

# Webhook
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    # Запускаем обработку через run
    asyncio.run(application.process_update(update))
    return "OK", 200

if __name__ == "__main__":
    application.initialize()  # важно инициализировать
    app.run(host="0.0.0.0", port=10000)
