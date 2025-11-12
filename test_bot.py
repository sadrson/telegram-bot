import os
from flask import Flask, request, jsonify
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes

# -------------------
# Переменные окружения
# -------------------
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    raise ValueError("Не задан BOT_TOKEN или CHAT_ID")

# -------------------
# Flask
# -------------------
app = Flask(__name__)

# -------------------
# Telegram Bot (синхронный)
# -------------------
bot = Bot(BOT_TOKEN)

def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    update.message.reply_text("Бот активен ✅")

application = Application.builder().token(BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))

# -------------------
# Webhook
# -------------------
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, bot)
        application.update_queue.put_nowait(update)
        return jsonify({"ok": True})
    except Exception as e:
        print("Ошибка webhook:", e)
        return jsonify({"ok": False, "error": str(e)}), 500

# -------------------
# Тестовое уведомление
# -------------------
@app.route("/", methods=["GET"])
def index():
    try:
        bot.send_message(chat_id=CHAT_ID, text="🥦 Тестовое уведомление! Бот работает ✅")
        print("✅ Уведомление отправлено")
    except Exception as e:
        print("❌ Ошибка отправки уведомления:", e)
    return "Бот онлайн", 200

# -------------------
# Запуск
# -------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
