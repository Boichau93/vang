import pandas as pd, numpy as np, statistics

def is_strong_doji(o,c,h,l,body_ratio=0.2,wick_body_ratio=2.0):
    rng = max(h-l,1e-9); body=abs(c-o)
    upper = h - max(c,o); lower = min(c,o)-l
    return (body/rng)<=body_ratio and (upper>=wick_body_ratio*body or lower>=wick_body_ratio*body)

def volume_confirm(vol_series, idx, lookback=10, soft=1.05, hard=1.3):
    if idx<lookback: return 0
    recent = vol_series.iloc[idx-lookback:idx]
    med = statistics.median([float(x) for x in recent if x==x])
    if med<=0: return 0
    r = float(vol_series.iloc[idx])/med
    if r>=hard: return 2
    if r>=soft: return 1
    return 0

def fractal_points(df):
    highs,lows=[],[]
    H,L=df['high'].values,df['low'].values
    for i in range(2,len(df)-2):
        if H[i]>H[i-1] and H[i]>H[i-2] and H[i]>H[i+1] and H[i]>H[i+2]: highs.append(H[i])
        if L[i]<L[i-1] and L[i]<L[i-2] and L[i]<L[i+1] and L[i]<L[i+2]: lows.append(L[i])
    return highs,lows

def cluster_levels(levels,width=0.2):
    if not levels: return []
    levels=sorted(levels); clusters=[[levels[0]]]
    for lv in levels[1:]:
        if abs(lv-clusters[-1][-1])<=width: clusters[-1].append(lv)
        else: clusters.append([lv])
    return [sum(g)/len(g) for g in clusters if len(g)>=2]

def get_strong_sr(df,width=0.2):
    h,l=fractal_points(df)
    return sorted(set(cluster_levels(h,width)+cluster_levels(l,width)))

def near_sr(price,sr_levels,percent_tol=0.002):
    for lv in sr_levels:
        if abs(price-lv)/price<=percent_tol: return True
    return False

def calc_atr(df,period=14):
    high_low = df['high']-df['low']
    high_close = (df['high']-df['close'].shift()).abs()
    low_close = (df['low']-df['close'].shift()).abs()
    tr = pd.concat([high_low,high_close,low_close],axis=1).max(axis=1)
    return tr.rolling(period).mean()

def suggest_sl_tp(entry,direction,atr,sl_mult=1.5,tp_mult=2.5):
    if atr is None or atr<=0: return None,None
    if direction=="BUY": sl=entry-atr*sl_mult; tp=entry+atr*tp_mult
    else: sl=entry+atr*sl_mult; tp=entry-atr*tp_mult
    return round(sl,5),round(tp,5)

def prepare_df(df):
    df=df.copy(); df.columns=[c.strip().lower() for c in df.columns]
    if 'time' in df.columns:
        df['time']=pd.to_datetime(df['time']); df.set_index('time',inplace=True)
    for col in ['open','high','low','close','volume']:
        if col not in df.columns: raise ValueError(f"Missing column: {col}")
    return df.dropna(subset=['open','high','low','close'])

def detect_strict_signals(df):
    df=prepare_df(df); df['atr']=calc_atr(df)
    sr=get_strong_sr(df); signals=[]
    for i in range(0,len(df)-1):
        o,h,l,c = df['open'].iloc[i],df['high'].iloc[i],df['low'].iloc[i],df['close'].iloc[i]
        if not is_strong_doji(o,c,h,l): continue
        if not near_sr(c,sr): continue
        score=2
        vol_idx=i+1; score+=volume_confirm(df['volume'],vol_idx)
        # EMA check
        slice_df=df.iloc[:i+2]
        ema20=slice_df['close'].ewm(span=20).mean().iloc[-1]
        ema50=slice_df['close'].ewm(span=50).mean().iloc[-1]
        if (ema20>ema50 and c>=o) or (ema20<ema50 and c<o): score+=1
        if score>=3:
            direction = "BUY" if c>=o else "SELL"
            entry_idx=vol_idx; entry_price=float(df['close'].iloc[entry_idx])
            atr_val = float(df['atr'].iloc[entry_idx]) if pd.notna(df['atr'].iloc[entry_idx]) else None
            sl,tp = suggest_sl_tp(entry_price,direction,atr_val)
            signals.append({'time':df.index[entry_idx],'price':entry_price,'direction':direction,'score':score,'atr':None if atr_val is None else round(atr_val,5),'sl':sl,'tp':tp})
        else:
            signals.append(None)
    return sr,signals
