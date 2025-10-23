import requests
import time
from flask import Flask
from threading import Thread

# === KEEP ALIVE ===
app = Flask('')

@app.route('/')
def home():
    return "I'm alive"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# === ТВОЙ БОТ ===

# 👉 Вставь сюда свой токен и chat_id
BOT_TOKEN = "8274488039:AAEBT6A-NSFMINjrM1ZboPg8Iq7Eh-K-XK0"
CHAT_ID = "-1003175445915"

# Текст уведомления
message = "🍕 Напоминание! Не забудь заполнить [форму](https://docs.google.com/forms/d/e/1FAIpQLSeG38n-P76ju46Zi6D4CHX8t6zfbxN506NupZboNeERhkT81A/viewform)."

# === Функция отправки сообщения ===
def send_message():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    response = requests.post(url, data=data)
    if response.ok:
        print("✅ Сообщение успешно отправлено!")
    else:
        print(f"⚠️ Ошибка при отправке: {response.text}")

# === ЗАПУСК ===
def main():
    keep_alive()  # <-- чтобы бот не засыпал на Replit
    print("🚀 Бот запущен, отправляю тестовое сообщение...")
    send_message()
    print("🤖 Бот ждёт времени для следующих уведомлений...")

    # пример — отправлять раз в 24 часа:
    while True:
        time.sleep(24 * 60 * 60)
        send_message()

if __name__ == "__main__":
    main()
