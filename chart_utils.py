
import json, requests

def send_chart_via_quickchart(token, chat_id, candles, title="Chart"):
    labels = [c['time'][-5:] for c in candles]
    closes = [c['close'] for c in candles]
    cfg = {
        "type": "line",
        "data": {"labels": labels, "datasets": [{"label":"Close","data":closes,"fill":False}]},
        "options": {"title": {"display": True, "text": title}}
    }
    url = "https://quickchart.io/chart"
    q = url + "?c=" + json.dumps(cfg, separators=(',',':'))
    requests.get(f"https://api.telegram.org/bot{token}/sendPhoto", params={
        "chat_id": chat_id,
        "photo": q,
        "caption": title
    })
