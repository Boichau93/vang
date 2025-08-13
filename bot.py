# bot.py
import telebot
from flask import Flask, request
import os

API_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "7998226455:AAFxZB7Khp-8zifrJNKL2-WdBCh4NXMHrb4")
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# Lệnh /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Xin chào! Gõ /scalp để chạy phân tích.")

# Lệnh /scalp
@bot.message_handler(commands=['scalp'])
def run_scalp(message):
    # TODO: Gọi hàm phân tích SCALP ở đây
    bot.reply_to(message, "📊 Đang chạy phân tích SCALP...")

# Nhận tin nhắn từ Telegram qua webhook
@app.route('/' + API_TOKEN, methods=['POST'])
def getMessage():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return 'ok', 200

# Trang kiểm tra bot
@app.route('/')
def index():
    return "Bot đang chạy!", 200

if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url='https://YOUR_RENDER_URL.onrender.com/' + API_TOKEN)
    app.run(host='0.0.0.0', port=5000)
