# fetch.py — download raw data with FAIL-FAST integrity guards (audit 2026-07-03)
# Data source (locked): Yahoo Finance via yfinance, auto_adjust=True
#   => "Close" = ADJUSTED close (splits + dividends) = TOTAL RETURN basis
import yfinance as yf, pandas as pd, json, sys, datetime, time

BASKETS = {
 "Semiconductors": ["NVDA","AMD","AVGO","TSM","QCOM","TXN","INTC","MRVL"],
 "Semi Equip & Memory": ["MU","WDC","STX","AMAT","LRCX","KLAC","ASML"],
 "Software": ["MSFT","ORCL","CRM","ADBE","NOW","PLTR","INTU","SNPS","CDNS"],
 "Mag 7": ["AAPL","MSFT","NVDA","AMZN","GOOGL","META","TSLA"],
 "Cybersecurity": ["CRWD","PANW","FTNT","ZS","OKTA"],
 "Genomics": ["CRSP","EDIT","BEAM","NTLA","ILMN","RXRX","TWST","PACB"],
 "Biotech Large": ["AMGN","GILD","VRTX","REGN","BIIB"],
 "Pharma & Managed Care": ["LLY","UNH","JNJ","MRK","ABBV","PFE"],
 "Defense": ["LMT","RTX","NOC","GD","LHX"],
 "Energy": ["XOM","CVX","COP","SLB","EOG"],
 "Banks & Brokers": ["JPM","GS","MS","BAC","WFC"],
 "Staples": ["PG","KO","PEP","COST","WMT"],
 "Utilities & Power": ["NEE","DUK","SO","VST","CEG"],
 "Materials": ["LIN","FCX","NUE","SHW","APD"],
 "AI Infra & Data Center": ["VRT","ETN","ANET","SMCI","DELL","CIEN"],
 "Quantum": ["IONQ","RGTI","QBTS"],
 "Nuclear & Uranium": ["CCJ","OKLO","SMR","LEU","BWXT"],
 "Gold Miners": ["NEM","AEM","GOLD","WPM"],
 "Solar": ["FSLR","ENPH","NXT","RUN"],
 "Crypto-linked": ["COIN","MSTR","HOOD","MARA","RIOT"],
 "Space & Drones": ["RKLB","ASTS","AVAV","KTOS","LUNR"],
 "China Tech ADR": ["BABA","PDD","BIDU","JD","BEKE"],
 "Homebuilders": ["DHI","LEN","PHM","TOL","NVR"],
 "Travel & Airlines": ["BKNG","ABNB","MAR","DAL","UAL","RCL"],
 "Fintech & Payments": ["V","MA","PYPL","AXP","COF"],
}
SECTORS = {"Tech (XLK)":"XLK","Health Care (XLV)":"XLV","Staples (XLP)":"XLP","Utilities (XLU)":"XLU","Materials (XLB)":"XLB","Energy (XLE)":"XLE","Financials (XLF)":"XLF","Industrials (XLI)":"XLI","Cons Discret (XLY)":"XLY","Comm Svcs (XLC)":"XLC","Real Estate (XLRE)":"XLRE"}

tickers = sorted(set(sum(BASKETS.values(), []) + list(SECTORS.values()) + ["SPY"]))
now_utc = datetime.datetime.now(datetime.timezone.utc)
print(len(tickers), "tickers | run", now_utc.isoformat())

data = yf.download(tickers, period="12mo", interval="1d", auto_adjust=True, progress=False, threads=True)
px = data["Close"].copy(); vol = data["Volume"].copy()

# ---- PHANTOM-ROW TRIM (added 2026-09-04) -----------------------------------
# Yahoo intermittently appends an all-NaN bar for a session that has not
# printed yet. Every ticker then looks stale on the last session, the repair
# pass can never clear it (Ticker.history has no such row either), and GUARD 3
# kills the run with all 148 tickers listed. This killed runs #51 and #52.
_real = px.dropna(how="all").index
if len(_real) == 0: print("FATAL: download returned no usable rows at all"); sys.exit(1)
_phantom = [str(d.date()) for d in px.index if d > _real[-1]]
if _phantom: print("PHANTOM rows trimmed:", _phantom)
px = px.loc[:_real[-1]].copy(); vol = vol.loc[:_real[-1]].copy()

# ---- REPAIR PASS (added 2026-08-12) ----------------------------------------
# yfinance's SQLite tz-cache can raise OperationalError('database is locked')
# when threads=True hammers it with 148 symbols. yfinance swallows it, logs
# "1 Failed download", and silently drops the symbol -> GUARD 1 kills the run.
# Seen on runs #32 and #33, both on MAR. Retry the casualties serially first.
def _bad(frame):
    out = [t for t in tickers if t not in frame.columns or frame[t].dropna().empty]
    last = frame.index[-1]
    out += [t for t in frame.columns if t not in out and pd.isna(frame.at[last, t])]
    return sorted(set(out))

repaired = []
bad = _bad(px)
for attempt in range(1, 4):
    if not bad:
        break
    print(f"REPAIR pass {attempt}: retrying {bad}")
    time.sleep(4)
    for t in bad:
        try:
            h = yf.Ticker(t).history(period="12mo", interval="1d", auto_adjust=True)
            if h.empty:
                continue
            c, vv = h["Close"], h["Volume"]
            c.index = c.index.tz_localize(None)
            vv.index = vv.index.tz_localize(None)
            px[t] = c.reindex(px.index)
            vol[t] = vv.reindex(vol.index)
            repaired.append(t)
        except Exception as e:
            print("  retry failed", t, repr(e))
    bad = _bad(px)
if repaired:
    print("REPAIR recovered:", sorted(set(repaired)))
if bad:
    print("REPAIR incomplete, still bad:", bad)

# ---- GUARD 1: no missing tickers (fail-fast, never publish partial baskets) ----
missing = [t for t in tickers if t not in px.columns or px[t].dropna().empty]
if missing:
    print("FATAL: missing tickers:", missing); sys.exit(1)

# ---- GUARD 2: stale-data detection ----
last_date = px.index[-1].date()
age_days = (now_utc.date() - last_date).days
if age_days > 4:  # allows weekend + 1 holiday
    print(f"FATAL: STALE DATA - last session {last_date} is {age_days} days old"); sys.exit(1)

# ---- GUARD 3: every ticker must have a fresh final row (no per-ticker staleness) ----
stale_tickers = px.iloc[-1][px.iloc[-1].isna()].index.tolist()
if stale_tickers:
    print("FATAL: tickers with no data on last session:", stale_tickers); sys.exit(1)

px.to_csv("prices.csv"); vol.to_csv("volume.csv")
json.dump({"baskets":BASKETS,"sectors":SECTORS}, open("universe.json","w"))
json.dump({
    "data_provider": "Yahoo Finance (yfinance)",
    "price_basis": "Adjusted Close (splits+dividends, total return)",
    "yfinance_version": yf.__version__, "pandas_version": pd.__version__,
    "python_version": sys.version.split()[0],
    "download_utc": now_utc.isoformat(), "asof_market_date": str(last_date),
    "tickers_requested": len(tickers), "tickers_ok": len(tickers) - len(missing),
    "rows": int(len(px)),
    "tickers_repaired": sorted(set(repaired)),
}, open("data_meta.json","w"), indent=1)
print("rows:", len(px), "| last session:", last_date, "| all guards passed")
