import os,json,urllib.parse
from utils import read_csv_safe, df_to_candles
from scalp_logic import detect_strict_signals

DATA_FOLDER = os.environ.get("DATA_FOLDER", r"C:\Users\Bach Kim\AppData\Roaming\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\MQL5\Files")
SYMBOL = os.environ.get("SYMBOL", "XAUUSD.v")
FILES = {"M5":f"{SYMBOL}_PERIOD_M5.csv","H1":f"{SYMBOL}_PERIOD_H1.csv","H4":f"{SYMBOL}_PERIOD_H4.csv"}

def quickchart_url(candles,title="Chart"):
    labels=[c['time'][-5:] for c in candles]; closes=[c['close'] for c in candles]
    cfg={"type":"line","data":{"labels":labels,"datasets":[{"label":"Close","data":closes,"fill":False}]},"options":{"title":{"display":True,"text":title}}}
    return "https://quickchart.io/chart?c="+urllib.parse.quote(json.dumps(cfg))

def run_full_analysis():
    lines=[f"🤖 AI SCALP Strict Report for {SYMBOL}"]
    charts=[]
    for tf,fname in FILES.items():
        path=os.path.join(DATA_FOLDER,fname)
        if not os.path.exists(path):
            lines.append(f"⚠ {tf}: file not found ({path})"); continue
        df=read_csv_safe(path)
        if len(df)<30:
            lines.append(f"⚠ {tf}: not enough data ({len(df)} rows)"); continue
        sr,signals=detect_strict_signals(df)
        latest=[s for s in signals if s is not None]; latest=latest[-1] if latest else None
        if latest:
            lines.append(f"• {tf}: {latest['direction']} @ {latest['price']:.3f} | score {latest['score']} | ATR {latest['atr']} | SL {latest['sl']} | TP {latest['tp']} | {latest['time']}")
        else:
            lines.append(f"• {tf}: no valid signal")
        candles=df_to_candles(df,n=120)
        charts.append((f"{SYMBOL} {tf}", quickchart_url(candles,title=f"{SYMBOL} {tf}")))
    return "\n".join(lines), charts
