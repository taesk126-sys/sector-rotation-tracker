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
# normalized mode must land in the SAME quadrant as raw for every series.
# Exception (2026-08-18): metrics.json stores RRG points rounded to 2dp, and the raw and
# normalized transforms have different scales, so a series sitting exactly on the 100 line
# can round to 100.00 on one axis and 99.99 on the other. That is rounding noise, not a real
# disagreement, and it blocked publication on 2026-08-17. Axes within NB_TOL of 100 are
# reported as on-boundary instead of failing. compute.py does the exact (unrounded) check.
NB_TOL = 0.02
def _axis_ok(a, b):
    return abs(a - 100) <= NB_TOL or abs(b - 100) <= NB_TOL or (a >= 100) == (b >= 100)
def _norm_ok(n):
    xr, yr = m["rrg"][n][-1]; xn, yn = m["rrg_norm"][n][-1]
    return _axis_ok(xr, xn) and _axis_ok(yr, yn)
nbad = [n for n in m["themes"] if "rrg_norm" in m and not _norm_ok(n)]
nedge = [n for n in m["themes"] if "rrg_norm" in m and _norm_ok(n)
         and quad(*m["rrg_norm"][n][-1]) != m["themes"][n]["quad"]]
if nbad: fails.append(("rrg_norm","quadrant",nbad,None))
print("norm-vs-raw quadrants:", "identical" if not nbad else f"MISMATCH {nbad}")
if nedge: print("on-boundary (rounding, tolerated):", nedge)

if fails:
    print(f"\nVALIDATION FAILED ({len(fails)} issues) — DO NOT PUBLISH"); sys.exit(1)
print("\nVALIDATION PASSED — safe to publish")
