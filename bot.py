
import os
from flask import Flask, request
import telebot
from scalp_analysis import run_full_analysis
from chart_utils import send_chart_via_quickchart

API_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "7998226455:AAFxZB7Khp-8zifrJNKL2-WdBCh4NXMHrb4")
DEFAULT_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "6226779521")

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

@bot.message_handler(commands=['start','help'])
def send_welcome(message):
    bot.reply_to(message, "Hello, I'm AI SCALP bot. Send /scalp to run analysis.")

@bot.message_handler(commands=['scalp'])
def handle_scalp(message):
    chat_id = message.chat.id
    bot.reply_to(message, "⏳ Running AI SCALP analysis...")
    try:
        report, charts = run_full_analysis()
        # send text report
        bot.send_message(chat_id, report)
        # send charts (list of (title, candles))
        for title, candles in charts:
            send_chart_via_quickchart(API_TOKEN, chat_id, candles, title=title)
        bot.send_message(chat_id, "✅ Analysis complete.")
    except Exception as e:
        bot.send_message(chat_id, f"❌ Error running analysis: {e}")

# Endpoint to receive Telegram updates
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
    # When run locally for testing you may set webhook manually or use ngrok.
    # In deployment (Render/etc.) ensure TELEGRAM_BOT_TOKEN env var is set.
    webhook_url = os.environ.get("WEBHOOK_URL")  # e.g. https://yourdomain.com/<API_TOKEN>
    try:
        bot.remove_webhook()
    except Exception:
        pass
    if webhook_url:
        bot.set_webhook(url=webhook_url.rstrip('/') + '/' + API_TOKEN)
        print("Webhook set to", webhook_url.rstrip('/') + '/' + API_TOKEN)
    # Start Flask app
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
