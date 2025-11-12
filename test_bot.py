from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ---------- Flask ----------
app = Flask(__name__)

# ---------- Telegram Bot ----------
BOT_TOKEN = "YOUR_BOT_TOKEN"  # Вставь сюда свой токен
application = ApplicationBuilder().token(BOT_TOKEN).build()

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот.")

# Регистрируем обработчик
application.add_handler(CommandHandler("start", start))

# ---------- Webhook endpoint ----------
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.create_task(application.process_update(update))
    return "OK", 200

# ---------- Главная страница ----------
@app.route("/", methods=["GET"])
def index():
    return "Бот работает!", 200

# ---------- Запуск (для локального теста) ----------
if __name__ == "__main__":
    app.run(port=10000)
