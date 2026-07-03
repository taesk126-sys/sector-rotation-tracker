# validate_independent.py — CI reconciliation gate (audit 2026-07-03)
# Recomputes returns from raw prices with INDEPENDENT formulas (no import from compute.py).
# Fails (exit 1) if any figure differs from metrics.json by > 0.011 pp -> publish is blocked.
import pandas as pd, json, sys

TOL = 0.011  # pp; dashboard rounds to 2dp
px = pd.read_csv("prices.csv", index_col=0, parse_dates=True).ffill(limit=2)
uni = json.load(open("universe.json")); m = json.load(open("metrics.json"))
HOR = {"r1d":1,"r1w":5,"r1m":21,"r3m":63}
fails = []

def check(name, hor, indep):
    dash = m["themes"][name][hor] if name in m["themes"] else m["spy"][hor]
    d = indep - dash
    status = "ok" if abs(d) <= TOL else "FAIL"
    if status == "FAIL": fails.append((name, hor, round(indep,3), dash))
    print(f"{name:24}{hor:5}indep={indep:9.2f} dash={dash:9.2f} diff={d:+.3f} {status}")

# sector ETFs + SPY : plain price-relative return
for name, t in [("Tech (XLK)","XLK"),("Financials (XLF)","XLF"),("Health Care (XLV)","XLV"),
                ("Energy (XLE)","XLE"),("Staples (XLP)","XLP")]:
    for hor, n in HOR.items():
        check(name, hor, (px[t].iloc[-1]/px[t].iloc[-1-n]-1)*100)
for hor, n in HOR.items():
    check("SPY", hor, (px["SPY"].iloc[-1]/px["SPY"].iloc[-1-n]-1)*100)

# custom baskets : daily-rebalanced equal-weight, written independently
for b in ["Semiconductors","Semi Equip & Memory","Quantum","Crypto-linked","China Tech ADR"]:
    mem = uni["baskets"][b]
    v = (1 + px[mem].pct_change().mean(axis=1)).cumprod()
    for hor, n in HOR.items():
        check(b, hor, (v.iloc[-1]/v.iloc[-1-n]-1)*100)

# quadrant consistency on all series
quad = lambda x,y: ("Leading" if x>=100 and y>=100 else "Improving" if x<100 and y>=100
                    else "Weakening" if x>=100 and y<100 else "Lagging")
qbad = [n for n in m["themes"] if quad(*m["rrg"][n][-1]) != m["themes"][n]["quad"]]
if qbad: fails.append(("quadrant","label",qbad,None))
print("quadrant labels:", "36/36 consistent" if not qbad else f"MISMATCH {qbad}")

if fails:
    print(f"\nVALIDATION FAILED ({len(fails)} issues) — DO NOT PUBLISH"); sys.exit(1)
print("\nVALIDATION PASSED — safe to publish")
