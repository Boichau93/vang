import os
from flask import Flask, request
import telebot
from scalp_analysis import run_full_analysis

API_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not API_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN env var not set")
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

@bot.message_handler(commands=['start','help'])
def send_welcome(message):
    bot.reply_to(message, "AI SCALP bot ready. Use /scalp to run the analysis.")

@bot.message_handler(commands=['scalp'])
def handle_scalp(message):
    chat_id = message.chat.id
    bot.reply_to(message, "⏳ Running AI SCALP strict analysis...")
    try:
        report, charts = run_full_analysis()
        for chunk in [report[i:i+3900] for i in range(0, len(report), 3900)]:
            bot.send_message(chat_id, chunk)
        for title, chart_url in charts:
            bot.send_photo(chat_id, chart_url)
        bot.send_message(chat_id, "✅ Analysis complete.")
    except Exception as e:
        bot.send_message(chat_id, f"❌ Error running analysis: {e}")

@app.route('/' + API_TOKEN, methods=['POST'])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return 'ok', 200

@app.route('/')
def index():
    return 'AI SCALP Webhook Bot is running', 200

if __name__ == "__main__":
    WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
    if WEBHOOK_URL:
        try:
            bot.remove_webhook()
        except Exception:
            pass
        bot.set_webhook(url=WEBHOOK_URL.rstrip('/') + '/' + API_TOKEN)
        print("Webhook set to", WEBHOOK_URL.rstrip('/') + '/' + API_TOKEN)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)))
