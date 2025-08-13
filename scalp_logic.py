
import numpy as np
import pandas as pd
import statistics

def is_doji(o, c, h, l, body_ratio_threshold=0.3):
    rng = max(h - l, 1e-9)
    body = abs(c - o)
    return (body / rng) <= body_ratio_threshold

def volume_score(vol_series, idx, lookback=5, soft_ratio=1.05, hard_ratio=1.30):
    if idx < lookback:
        return 0
    recent = vol_series.iloc[idx - lookback: idx]
    med = statistics.median([float(x) for x in recent if x == x])
    if med <= 0:
        return 0
    ratio = float(vol_series.iloc[idx]) / med
    if ratio >= hard_ratio:
        return 2
    if ratio >= soft_ratio:
        return 1
    return 0

def fractal_points(df):
    highs, lows = [], []
    H, L = df['high'].values, df['low'].values
    for i in range(2, len(df)-2):
        if H[i] > H[i-1] and H[i] > H[i+1] and H[i] > H[i-2] and H[i] > H[i+2]:
            highs.append((df.index[i], H[i]))
        if L[i] < L[i-1] and L[i] < L[i+1] and L[i] < L[i-2] and L[i] < L[i+2]:
            lows.append((df.index[i], L[i]))
    return highs, lows

def cluster_levels(levels, cluster_width=2.0):
    if not levels:
        return []
    levels = sorted([lv for _, lv in levels])
    clusters = [[levels[0]]]
    for lv in levels[1:]:
        if abs(lv - clusters[-1][-1]) <= cluster_width:
            clusters[-1].append(lv)
        else:
            clusters.append([lv])
    centers = [sum(g)/len(g) for g in clusters if len(g) >= 2]
    return centers

def strong_sr_levels(df, cluster_width=2.0):
    highs, lows = fractal_points(df)
    return sorted(set(cluster_levels(highs, cluster_width) + cluster_levels(lows, cluster_width)))

def near_sr(price, sr_levels, tolerance=0.5):
    return any(abs(price - lv) <= tolerance for lv in sr_levels)

def calc_atr(df, period=14):
    high_low = df['high'] - df['low']
    high_close_prev = (df['high'] - df['close'].shift()).abs()
    low_close_prev = (df['low'] - df['close'].shift()).abs()
    tr = pd.concat([high_low, high_close_prev, low_close_prev], axis=1).max(axis=1)
    atr = tr.rolling(period).mean()
    return atr

def suggest_sl_tp(entry_price, direction, atr_value, atr_mult_sl=1.2, rr=1.5):
    if atr_value is None or atr_value <= 0:
        return None, None
    if direction == "BUY":
        sl = entry_price - atr_value * atr_mult_sl
        tp = entry_price + atr_value * rr
    else:
        sl = entry_price + atr_value * atr_mult_sl
        tp = entry_price - atr_value * rr
    return round(sl, 2), round(tp, 2)

def prepare_df(df):
    df = df.copy()
    df.columns = [c.strip().lower() for c in df.columns]
    if 'time' in df.columns:
        df['time'] = pd.to_datetime(df['time'])
        df.set_index('time', inplace=True)
    for col in ['open','high','low','close','volume']:
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")
    df = df.dropna(subset=['open','high','low','close'])
    return df

def detect_signals(df, sr_width=2.0, sr_tolerance=0.5, atr_period=14, atr_mult_sl=1.2, rr=1.5):
    df = prepare_df(df)
    df['atr'] = calc_atr(df, period=atr_period)
    sr = strong_sr_levels(df, cluster_width=sr_width)
    signals = []
    for i in range(len(df)):
        o, h, l, c = df['open'].iloc[i], df['high'].iloc[i], df['low'].iloc[i], df['close'].iloc[i]
        score = 0
        if is_doji(o, c, h, l) and near_sr(c, sr, tolerance=sr_tolerance):
            score += 2
        vol_idx = i+1 if i+1 < len(df) else i
        try:
            score += volume_score(df['volume'], vol_idx)
        except Exception:
            pass
        if score >= 3:
            direction = 'BUY' if c >= o else 'SELL'
            entry_idx = vol_idx
            entry_time = df.index[entry_idx]
            entry_price = float(df['close'].iloc[entry_idx])
            atr_val = float(df['atr'].iloc[entry_idx]) if pd.notna(df['atr'].iloc[entry_idx]) else None
            sl, tp = suggest_sl_tp(entry_price, direction, atr_val, atr_mult_sl=atr_mult_sl, rr=rr)
            signals.append({
                'index': entry_time,
                'price': entry_price,
                'direction': direction,
                'score': score,
                'atr': None if atr_val is None else round(atr_val, 2),
                'sl': sl,
                'tp': tp
            })
        else:
            signals.append(None)
    return sr, signals
