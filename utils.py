import pandas as pd
def read_csv_safe(path):
    for enc in ("utf-8-sig","utf-8","cp1252"):
        try: return pd.read_csv(path, encoding=enc)
        except Exception: pass
    return pd.read_csv(path)
def df_to_candles(df,n=120):
    df=df.tail(n).copy(); df.columns=[c.strip().lower() for c in df.columns]
    if 'time' in df.columns:
        df['time']=pd.to_datetime(df['time']); df.set_index('time',inplace=True)
    out=[]
    for t,row in df.iterrows():
        out.append({"time":t.strftime("%Y-%m-%d %H:%M"),"open":float(row["open"]),"high":float(row["high"]),"low":float(row["low"]),"close":float(row["close"]),"volume":float(row.get("volume",0.0))})
    return out
