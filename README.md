
# AI_SCALP_WEBHOOK

This package runs a Flask webhook Telegram bot that responds to `/scalp` and runs the AI scalp analysis (Doji + SR + Volume + ATR SL/TP) reading CSVs exported by MT5.

## Files
- `bot.py` - Flask webhook + telebot handlers.
- `scalp_analysis.py` - orchestrates reading CSV and running logic.
- `scalp_logic.py` - detection logic (Doji, SR, Volume, ATR, SL/TP).
- `chart_utils.py` - uses QuickChart to generate charts and send to Telegram.
- `utils.py` - CSV reader and helper to convert DataFrame to candles.
- `requirements.txt` - Python dependencies.

## Deploy on Render (quick)
1. Push this repo to GitHub.
2. Create a new Web Service on Render, connect to repo.
3. Set Environment Variables:
   - `TELEGRAM_BOT_TOKEN` (required)
   - `TELEGRAM_CHAT_ID` (optional)
   - `DATA_FOLDER` (optional) default points to MT5 Common Files folder.
4. Start Command: `python bot.py`
Render provides HTTPS domain; set `WEBHOOK_URL` env var to `https://<your-render-domain>` so the bot will set webhook automatically.

## Local testing
You can test locally using ngrok and set `WEBHOOK_URL` to your ngrok https URL.
