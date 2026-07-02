import pandas as pd, numpy as np, json

D = ""
px = pd.read_csv(D+"prices.csv", index_col=0, parse_dates=True)
vol = pd.read_csv(D+"volume.csv", index_col=0, parse_dates=True)
uni = json.load(open(D+"universe.json"))
BASKETS, SECTORS = uni["baskets"], uni["sectors"]

px = px.ffill()
# equal-weight basket index (normalized to 100 at start of common window)
def basket_index(members):
    members = [t for t in members if t in px.columns and px[t].notna().sum() > 60]
    sub = px[members].dropna(how="all")
    norm = sub / sub.iloc[0] * 100
    return norm.mean(axis=1)

series = {}
for name, mem in BASKETS.items(): series[name] = basket_index(mem)
for name, tkr in SECTORS.items(): series[name] = px[tkr] / px[tkr].iloc[0] * 100
spy = px["SPY"] / px["SPY"].iloc[0] * 100
idx = pd.DataFrame(series).dropna()

def ret(s, n): return (s.iloc[-1] / s.iloc[-1-n] - 1) * 100

rows = {}
for name, s in idx.items():
    rows[name] = {"r1d": ret(s,1), "r1w": ret(s,5), "r1m": ret(s,21), "r3m": ret(s,63)}
spy_r = {"r1d": ret(spy,1), "r1w": ret(spy,5), "r1m": ret(spy,21), "r3m": ret(spy,63)}

# RRG: RS ratio vs SPY, smoothed
def rrg(s, n_trail=8, step=5):
    rs = s / spy
    rs_ratio = 100 * rs / rs.rolling(63).mean()
    rs_mom = 100 * rs_ratio / rs_ratio.shift(10)
    pts = []
    for k in range(n_trail-1, -1, -1):
        i = -1 - k*step
        pts.append([round(float(rs_ratio.iloc[i]),2), round(float(rs_mom.iloc[i]),2)])
    return pts  # oldest -> newest, weekly steps

rrg_data = {name: rrg(s) for name, s in idx.items()}

# breadth + dollar-volume shift for stock baskets
breadth = {}
for name, mem in BASKETS.items():
    sub = px[mem]
    ma20 = sub.rolling(20).mean()
    above = (sub.iloc[-1] > ma20.iloc[-1]).mean() * 100
    dv = (px[mem] * vol[mem])
    dv5 = dv.iloc[-5:].sum().sum(); dv20 = dv.iloc[-25:-5].sum().sum()/4
    breadth[name] = {"pct_above_20dma": round(float(above),1),
                     "dollar_vol_ratio": round(float(dv5/dv20),2)}

quad = lambda x,y: ("Leading" if x>=100 and y>=100 else "Improving" if x<100 and y>=100 else "Weakening" if x>=100 and y<100 else "Lagging")
out = {"asof": str(idx.index[-1].date()), "spy": {k: round(v,2) for k,v in spy_r.items()},
       "themes": {}, "rrg": rrg_data, "breadth": breadth,
       "is_sector": {n: (n in SECTORS) for n in idx.columns}}
for name in idx.columns:
    r = rows[name]
    x,y = rrg_data[name][-1]
    out["themes"][name] = {**{k: round(v,2) for k,v in r.items()},
        "rel1m": round(r["r1m"]-spy_r["r1m"],2), "quad": quad(x,y)}
json.dump(out, open(D+"metrics.json","w"))

df = pd.DataFrame(out["themes"]).T.sort_values("r1m", ascending=False)
print("AS OF:", out["asof"], "| SPY 1D %.2f 1W %.2f 1M %.2f 3M %.2f" % tuple(spy_r.values()))
print(df.to_string())
print("\nBREADTH:"); print(pd.DataFrame(breadth).T.to_string())
