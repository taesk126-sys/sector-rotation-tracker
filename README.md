# US Sector & Theme Rotation Tracker

Dashboard ติดตาม sector/theme rotation ของตลาดหุ้นสหรัฐ อัปเดตอัตโนมัติทุกเช้าหลังตลาดปิด (GitHub Actions, cron 22:10 UTC จ.-ศ.)
Live: https://taesk126-sys.github.io/sector-rotation-tracker/

## Methodology (locked, audit 2026-07-03)
- **Data**: Yahoo Finance (yfinance, pinned) — **Adjusted Close** (splits+dividends = total return), 12mo daily. Fail-fast guards: missing ticker / stale data / per-ticker gap → ไม่ publish
- **Horizons**: 1D/1W/1M/3M = 1/5/21/63 **trading sessions**
- **Theme baskets**: **equal-weight daily-rebalanced analytical basket** — `index_t = Π(1 + mean(daily returns))` ไม่รวมต้นทุนซื้อขาย ไม่ใช่ผลตอบแทน ETF จริง
- **RRG-style map (custom, ไม่ใช่ JdK มาตรฐาน)** — 2 โหมด, quadrant เหมือนกันเป๊ะ (sign-preserving):
  - Raw: `RS-Ratio = 100×(idx/SPY)÷SMA63` , `RS-Momentum = 100×Ratio_t÷Ratio_{t-10}`
  - Normalized: `100 + (rs−SMA63)/SD63` , `100 + d/SD63(d)` โดย `d = Ratio_t − Ratio_{t-10}` (1 หน่วย = 1 SD ของตัวเอง)
  - Trail: 8 จุด ทุก 5 วันทำการ ยึด session ล่าสุด • Boundary: (100,100) → Leading
- **1M Excess vs SPY**: ลบกันตรง ๆ หน่วย percentage points
- **Breadth**: % สมาชิกที่ Adjusted Close > SMA20 (threshold เดียวทั้งจอ: เขียว ≥50 / เหลือง 30–50 / แดง <30)
- **Dollar Volume**: Σ(adjClose×vol) 5 วันล่าสุด ÷ ค่าเฉลี่ยบล็อก 5 วันของ 20 วันก่อนหน้า — วัด activity ไม่บอกทิศทาง

## Reproducibility
- `validate_independent.py` คำนวณซ้ำอิสระทุกวันใน CI — คลาดเกิน 0.011pp = ไม่ publish
- publish รายวัน: `metrics.json`, `universe.json`, `manifest.json` (SHA-256 + commit + versions), `data_meta.json`
- raw snapshots เก็บเป็น Actions artifact 90 วัน

เครื่องมือประกอบการวิเคราะห์ ไม่ใช่คำแนะนำการลงทุน
