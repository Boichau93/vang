
import os, pandas as pd
from utils import read_csv_safe, df_to_candles
from scalp_logic import detect_signals

# Config (can also be set via env or imported from config)
DATA_FOLDER = os.environ.get("DATA_FOLDER", r"C:\Users\Bach Kim\AppData\Roaming\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\MQL5\Files")
SYMBOL = os.environ.get("SYMBOL", "XAUUSD.v")
FILES = {
    "M5": f"{SYMBOL}_PERIOD_M5.csv",
    "H1": f"{SYMBOL}_PERIOD_H1.csv",
    "H4": f"{SYMBOL}_PERIOD_H4.csv"
}

def run_full_analysis():
    report_lines = [f"🤖 AI SCALP Report for {SYMBOL}"]
    charts = []
    for tf, fname in FILES.items():
        path = os.path.join(DATA_FOLDER, fname)
        if not os.path.exists(path):
            report_lines.append(f"⚠ {tf}: file not found ({path})")
            continue
        df = read_csv_safe(path)
        if len(df) < 20:
            report_lines.append(f"⚠ {tf}: not enough data ({len(df)} rows)")
            continue
        sr, signals = detect_signals(df)
        latest = [s for s in signals if s is not None]
        latest = latest[-1] if latest else None
        if latest:
            report_lines.append(f"• {tf}: {latest['direction']} @ {latest['price']:.2f} | score {latest['score']} | ATR {latest['atr']} | SL {latest['sl']} | TP {latest['tp']} | {latest['index']}")
        else:
            report_lines.append(f"• {tf}: no valid signal")
        candles = df_to_candles(df, n=120)
        charts.append((f"{SYMBOL} {tf}", candles))
    report = "\\n".join(report_lines)
    return report, charts
