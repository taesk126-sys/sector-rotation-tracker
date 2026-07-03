# compute.py — all metrics (audit-locked version, 2026-07-03)
import pandas as pd, numpy as np, json, sys

# ================= LOCKED PARAMETERS (do not change without re-audit) =================
# Return horizons in TRADING SESSIONS (not calendar): 1D/1W/1M/3M = 1/5/21/63
HORIZONS = {"r1d": 1, "r1w": 5, "r1m": 21, "r3m": 63}
# RRG (CUSTOM, not JdK-standard):
#   RS-Ratio    = 100 * (idx/SPY) / SMA(idx/SPY, RS_WINDOW sessions)   on DAILY series
#   RS-Momentum = 100 * RSRatio_t / RSRatio_{t-MOM_LAG sessions}       on DAILY series
#   trail: TRAIL_N points, every TRAIL_STEP sessions, anchored at LATEST session
RS_WINDOW, MOM_LAG, TRAIL_N, TRAIL_STEP = 63, 10, 8, 5
MIN_SESSIONS = RS_WINDOW + MOM_LAG + (TRAIL_N - 1) * TRAIL_STEP + 2   # = 110
# Basket methodology: EQUAL-WEIGHT DAILY-REBALANCED analytical basket
#   basket_index_t = cumprod(1 + mean_members(daily_return))
#   (no transaction costs; NOT an investable ETF return)
# Prices: Adjusted Close (total return) — see data_meta.json
# rel1m = ARITHMETIC excess return in percentage points: r1m_theme - r1m_SPY
RS_SANITY_BAND = 15.0   # warn when |RS-Ratio - 100| exceeds this
# =======================================================================================

px  = pd.read_csv("prices.csv", index_col=0, parse_dates=True)
vol = pd.read_csv("volume.csv", index_col=0, parse_dates=True)
uni = json.load(open("universe.json"))
try: data_meta = json.load(open("data_meta.json"))
except FileNotFoundError: data_meta = {}
BASKETS, SECTORS = uni["baskets"], uni["sectors"]

# ---- integrity: every ticker must exist, have enough history, and a fresh last row ----
problems = []
for t in sorted(set(sum(BASKETS.values(), []) + list(SECTORS.values()) + ["SPY"])):
    if t not in px.columns: problems.append(f"{t}: not in prices.csv")
    elif px[t].notna().sum() < MIN_SESSIONS: problems.append(f"{t}: only {int(px[t].notna().sum())} sessions (<{MIN_SESSIONS})")
    elif pd.isna(px[t].iloc[-1]): problems.append(f"{t}: NaN on last session")
if problems:
    print("FATAL: data integrity failed:\n  " + "\n  ".join(problems)); sys.exit(1)

n_gaps = int(px.isna().sum().sum())
px = px.ffill(limit=2)      # bridge isolated 1-2 session gaps ONLY; logged in metadata
if px.isna().any().any():   # gaps longer than 2 sessions are not acceptable
    bad = px.columns[px.isna().any()].tolist()
    print("FATAL: unfilled gaps >2 sessions:", bad); sys.exit(1)

# ---- basket index: equal-weight, DAILY-REBALANCED ----
def basket_index(members):
    daily_ret = px[members].pct_change()
    return (1 + daily_ret.mean(axis=1)).cumprod() * 100

series = {name: basket_index(mem) for name, mem in BASKETS.items()}
for name, tkr in SECTORS.items(): series[name] = px[tkr] / px[tkr].iloc[0] * 100
spy = px["SPY"] / px["SPY"].iloc[0] * 100
idx = pd.DataFrame(series).dropna()

def ret(s, n): return (s.iloc[-1] / s.iloc[-1-n] - 1) * 100

rows  = {name: {h: ret(s, n) for h, n in HORIZONS.items()} for name, s in idx.items()}
spy_r = {h: ret(spy, n) for h, n in HORIZONS.items()}

def rrg(s):
    rs = s / spy
    rs_ratio = 100 * rs / rs.rolling(RS_WINDOW).mean()
    rs_mom   = 100 * rs_ratio / rs_ratio.shift(MOM_LAG)
    return [[round(float(rs_ratio.iloc[-1-k*TRAIL_STEP]), 2), round(float(rs_mom.iloc[-1-k*TRAIL_STEP]), 2)]
            for k in range(TRAIL_N-1, -1, -1)]
rrg_data = {name: rrg(s) for name, s in idx.items()}

breadth = {}
for name, mem in BASKETS.items():
    sub = px[mem]                       # complete by construction (guards above)
    above = (sub.iloc[-1] > sub.rolling(20).mean().iloc[-1]).mean() * 100
    dv = px[mem] * vol[mem]             # PROXY: adjusted close x volume (not true traded value)
    dv5 = dv.iloc[-5:].sum().sum(); dv20 = dv.iloc[-25:-5].sum().sum() / 4
    breadth[name] = {"pct_above_20dma": round(float(above), 1),
                     "dollar_vol_ratio": round(float(dv5 / dv20), 2)}

# quadrant: boundary policy — x=100,y=100 counts as Leading
quad = lambda x, y: ("Leading" if x >= 100 and y >= 100 else "Improving" if x < 100 and y >= 100
                     else "Weakening" if x >= 100 and y < 100 else "Lagging")

warnings = [f"{n}: RS-Ratio {rrg_data[n][-1][0]}" for n in idx.columns
            if abs(rrg_data[n][-1][0] - 100) > RS_SANITY_BAND]

out = {"asof": str(idx.index[-1].date()),
       "spy": {k: round(v, 2) for k, v in spy_r.items()},
       "themes": {}, "rrg": rrg_data, "breadth": breadth,
       "is_sector": {n: (n in SECTORS) for n in idx.columns},
       "meta": {**data_meta,
                "methodology": "equal-weight daily-rebalanced analytical basket; adjusted close (total return); horizons 1/5/21/63 trading sessions; RRG custom SMA63/ROC10 daily; rel1m arithmetic pp",
                "params": {"RS_WINDOW": RS_WINDOW, "MOM_LAG": MOM_LAG, "TRAIL_N": TRAIL_N, "TRAIL_STEP": TRAIL_STEP},
                "ffilled_cells": n_gaps, "rs_sanity_warnings": warnings}}
for name in idx.columns:
    r = rows[name]; x, y = rrg_data[name][-1]
    out["themes"][name] = {**{k: round(v, 2) for k, v in r.items()},
                           "rel1m": round(r["r1m"] - spy_r["r1m"], 2), "quad": quad(x, y)}

# ---- built-in asserts before publishing ----
for n, d in out["themes"].items():
    assert d["quad"] == quad(*out["rrg"][n][-1]), f"quadrant mismatch {n}"
    assert all(v is not None and not (isinstance(v, float) and np.isnan(v)) for v in d.values() if not isinstance(v, str)), f"NaN in {n}"
json.dump(out, open("metrics.json", "w"))
if warnings: print("SANITY WARNINGS:", warnings)
print("AS OF:", out["asof"], "| themes:", len(out["themes"]), "| all asserts passed")
print(pd.DataFrame(out["themes"]).T.sort_values("r1m", ascending=False).to_string())
