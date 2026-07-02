import json

D = ""
m = json.load(open(D+"metrics.json"))
DATA = json.dumps(m, ensure_ascii=False)

html = """<!DOCTYPE html>
<html lang="th"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sector Rotation Tracker — SuperTrader</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
:root{--bg:#0d1117;--card:#161b22;--line:#2d333b;--txt:#e6edf3;--dim:#8b949e;--org:#f0a840;
--green:#3fb950;--red:#f85149;--blue:#58a6ff;--yellow:#d29922}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--txt);
font-family:-apple-system,'Segoe UI',Roboto,'Noto Sans Thai',sans-serif}
header{padding:18px 24px;border-bottom:1px solid var(--line);display:flex;justify-content:space-between;align-items:baseline;flex-wrap:wrap}
h1{font-size:20px;margin:0;color:var(--org)}#asof{color:var(--dim);font-size:13px}
.wrap{display:grid;grid-template-columns:1.1fr 1fr;gap:16px;padding:16px 24px;max-width:1400px;margin:auto}
@media(max-width:980px){.wrap{grid-template-columns:1fr}}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px}
.card h2{font-size:14px;margin:0 0 10px;color:var(--org);font-weight:600}
.tabs{display:flex;gap:6px;margin-bottom:10px;flex-wrap:wrap}
.tabs button{background:#21262d;border:1px solid var(--line);color:var(--dim);padding:4px 12px;border-radius:14px;cursor:pointer;font-size:12px}
.tabs button.on{background:var(--org);color:#000;border-color:var(--org);font-weight:600}
.hm{width:100%;border-collapse:collapse;font-size:12.5px}
.hm th{color:var(--dim);text-align:right;padding:5px 7px;font-weight:500;border-bottom:1px solid var(--line)}
.hm th:first-child,.hm td:first-child{text-align:left}
.hm td{padding:5px 7px;text-align:right;border-bottom:1px solid #1c2128;cursor:default}
.hm td.name{color:var(--org);white-space:nowrap}
.badge{font-size:10px;padding:1px 7px;border-radius:9px;margin-left:6px;vertical-align:middle}
.q-Leading{background:#1a3a1f;color:#3fb950}.q-Improving{background:#1a2f4a;color:#58a6ff}
.q-Weakening{background:#4a3a15;color:#d29922}.q-Lagging{background:#4a1a1a;color:#f85149}
canvas{max-width:100%}
.note{color:var(--dim);font-size:11.5px;margin-top:8px;line-height:1.5}
.bcell{display:flex;align-items:center;gap:8px}.bar{height:7px;border-radius:4px;background:#21262d;flex:1;overflow:hidden}
.bar i{display:block;height:100%;border-radius:4px}
.full{grid-column:1/-1}
.pb{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}
@media(max-width:980px){.pb{grid-template-columns:repeat(2,1fr)}}
.pbcol{background:#0d1117;border:1px solid var(--line);border-radius:8px;padding:10px 12px}
.pbcol h3{font-size:13px;margin:0 0 6px}.pbcol p{font-size:11.5px;color:var(--dim);line-height:1.55;margin:0 0 8px}
.chip{display:inline-block;font-size:11px;padding:2px 8px;margin:2px 3px 2px 0;border-radius:10px;background:#21262d;color:var(--txt)}
.chip b{color:var(--org);font-weight:600}
.chip i{font-style:normal;font-size:10px;color:var(--dim);margin-left:3px}
.chip-good{border-left:3px solid var(--green)}.chip-mid{border-left:3px solid var(--yellow)}
.chip-bad{border-left:3px solid var(--red)}.chip-etf{border-left:3px solid #444c56}
.sub{font-size:11px;margin:7px 0 3px;font-weight:600;color:var(--dim)}
.dyn{color:var(--yellow)}
.apx{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
@media(max-width:980px){.apx{grid-template-columns:1fr}}
.apxb{background:#0d1117;border:1px solid var(--line);border-radius:8px;padding:9px 11px}
.apxb h4{margin:0 0 6px;font-size:12.5px;color:var(--org)}
.etfc{display:inline-block;font-size:11px;padding:2px 8px;margin:2px 4px 2px 0;border-radius:10px;background:#21262d;border-left:3px solid var(--org)}
.etfc b{color:var(--txt)}
.mem{font-size:10.5px;color:var(--dim);margin-top:6px;line-height:1.5}

</style></head><body>
<header><h1>🔄 US Sector &amp; Theme Rotation Tracker</h1><div id="asof"></div></header>
<div class="wrap">
<div class="card"><h2>Relative Rotation Graph (เทียบ SPY, หางย้อนหลัง 8 สัปดาห์)</h2>
<div class="tabs" id="rrgTabs"><button data-f="theme" class="on">ธีม</button><button data-f="sector">Sector ETF</button><button data-f="all">ทั้งหมด</button></div>
<canvas id="rrg" height="330"></canvas>
<div class="note">แกน X = RS-Ratio (แรงเทียบตลาดปัจจุบัน) • แกน Y = RS-Momentum (โมเมนตัมของแรงนั้น) •
เขียว Leading = แข็งและยังแรงขึ้น • ฟ้า Improving = ยังอ่อนแต่กำลังฟื้น (เงินเริ่มไหลเข้า) •
เหลือง Weakening = ยังแข็งแต่แผ่ว (เงินเริ่มไหลออก) • แดง Lagging = อ่อนและยังแย่ลง จุดใหญ่คือสัปดาห์ล่าสุด</div></div>
<div class="card"><h2>Heatmap ผลตอบแทนรายธีม (equal-weight)</h2>
<div class="tabs" id="hmTabs"><button data-k="r1m" class="on">เรียงตาม 1M</button><button data-k="r1w">1W</button><button data-k="r1d">1D</button><button data-k="rel1m">1M เทียบ SPY</button></div>
<table class="hm" id="hmT"></table></div>
<div class="card full"><h2>🎯 Momentum Playbook — เล่นตาม rotation ยังไง</h2>
<div class="pb">
<div class="pbcol" style="border-top:3px solid var(--green)"><h3 style="color:var(--green)">Leading — ถือต่อ / เล่นโมเมนตัม</h3>
<p>กลุ่มที่แข็งกว่าตลาดและยังแรงขึ้น เหมาะสุดสำหรับสาย momentum แต่ต้องดู RS-Momentum (แกน Y) ประกอบ ถ้าเริ่มโค้งลงใกล้ 100 แปลว่ากำลังจะเปลี่ยนเป็น Weakening ให้เตรียมแผนออก</p><div id="q-Leading"></div></div>
<div class="pbcol" style="border-top:3px solid var(--blue)"><h3 style="color:var(--blue)">Improving — จุดเข้าที่ risk/reward ดีสุด</h3>
<p>ยังอ่อนกว่าตลาดแต่โมเมนตัมกลับทิศแล้ว คือ "เงินเริ่มไหลเข้าแต่ราคายังไม่แพง" สายซื้อก่อนฝูงชนเล่นตรงนี้ จุดยืนยันคือหางบนกราฟชี้ขึ้นต่อเนื่อง 2-3 สัปดาห์ + breadth เริ่มฟื้น</p><div id="q-Improving"></div></div>
<div class="pbcol" style="border-top:3px solid var(--yellow)"><h3 style="color:var(--yellow)">Weakening — ทยอยขาย ห้ามเพิ่มไม้</h3>
<p>ยังแข็งกว่าตลาดอยู่ (ผลตอบแทนสะสมยังสวย) แต่แรงส่งแผ่วลง คือโซนที่คนติดดอยเยอะสุดเพราะ "ผลตอบแทนสะสมยังสวย กราฟยังดูดี" ทั้งที่เงินเริ่มออกแล้ว ถ้าจะช้อนให้รอมันวนลง Lagging แล้วกลับขึ้น Improving ก่อน <span class="dyn" id="dyn-weak"></span></p><div id="q-Weakening"></div></div>
<div class="pbcol" style="border-top:3px solid var(--red)"><h3 style="color:var(--red)">Lagging — ห้ามรีบช้อน</h3>
<p>อ่อนกว่าตลาดและยังแย่ลง สาย momentum ข้ามไปเลย เด้งแรงรายสัปดาห์ในโซนนี้ส่วนใหญ่คือ dead cat bounce จะน่าสนใจก็ต่อเมื่อขยับข้ามขึ้นไป Improving เท่านั้น</p><div id="q-Lagging"></div></div>
</div>
<div class="note">ขอบสีของป้าย = สุขภาพ breadth (เขียว &ge;50% ของสมาชิกยืนเหนือ 20DMA &bull; เหลือง 30-50% &bull; แดง &lt;30% &bull; เทา = Sector ETF ไม่มีค่า breadth) ตัวเลข B คือ % สมาชิกเหนือ 20DMA &bull; วงจรปกติหมุนตามเข็มนาฬิกา: Improving → Leading → Weakening → Lagging → กลับมา Improving ใหม่ • ป้ายในแต่ละช่องเรียงตามความแข็งเทียบ SPY (1M) • นี่คือกรอบวิเคราะห์ ไม่ใช่คำแนะนำซื้อขายรายตัว</div></div>
<div class="card full"><h2>Breadth &amp; Volume — สัญญาณเตือนก่อนราคา</h2>
<table class="hm" id="brT"></table>
<div class="note">% เหนือ 20DMA ต่ำ = สมาชิกในธีมหลุดแนวโน้มระยะสั้นเกือบหมด (แม้ราคาตะกร้ายังไม่พังมาก) •
Dollar Volume Ratio &gt; 1 = เม็ดเงินซื้อขาย 5 วันล่าสุดหนาแน่นกว่าค่าเฉลี่ยเดือนก่อน = เงินกำลังวิ่งเข้ามาเล่นกลุ่มนี้</div></div>
</div>
<script>
const M = __DATA__;
document.getElementById('asof').textContent = 'ข้อมูล ณ ' + M.asof + ' (ราคาปิด/ล่าสุด) • SPY 1D ' + M.spy.r1d + '% | 1M ' + M.spy.r1m + '% | 3M ' + M.spy.r3m + '%';
const QC = {Leading:'#3fb950',Improving:'#58a6ff',Weakening:'#d29922',Lagging:'#f85149'};
const names = Object.keys(M.themes);

// ---- RRG ----
let rrgChart=null;
function drawRRG(filter){
  const sel = names.filter(n => filter==='all' || (filter==='sector')===M.is_sector[n]);
  const ds = [];
  sel.forEach(n=>{
    const pts = M.rrg[n]; const q = M.themes[n].quad; const c = QC[q];
    ds.push({label:n, data:pts.map(p=>({x:p[0],y:p[1]})), showLine:true, borderColor:c+'55',
      backgroundColor:pts.map((_,i)=> i===pts.length-1 ? c : c+'44'),
      pointRadius:pts.map((_,i)=> i===pts.length-1 ? 7 : 2.5), borderWidth:1.5, tension:.3});
  });
  if(rrgChart) rrgChart.destroy();
  const ctx = document.getElementById('rrg');
  rrgChart = new Chart(ctx,{type:'scatter',data:{datasets:ds},options:{
    animation:false,plugins:{legend:{display:false},tooltip:{callbacks:{label:i=>i.dataset.label+' ('+M.themes[i.dataset.label].quad+') RS '+i.parsed.x.toFixed(1)+' / Mom '+i.parsed.y.toFixed(1)}}},
    scales:{x:{title:{display:true,text:'RS-Ratio',color:'#8b949e'},grid:{color:'#21262d'},ticks:{color:'#8b949e'}},
            y:{title:{display:true,text:'RS-Momentum',color:'#8b949e'},grid:{color:'#21262d'},ticks:{color:'#8b949e'}}}
  },plugins:[{id:'quad',beforeDraw(c){const {ctx,chartArea:a,scales:{x,y}}=c;if(!a)return;
    const cx=x.getPixelForValue(100),cy=y.getPixelForValue(100);ctx.save();
    ctx.fillStyle='#3fb95012';ctx.fillRect(cx,a.top,a.right-cx,cy-a.top);
    ctx.fillStyle='#58a6ff10';ctx.fillRect(a.left,a.top,cx-a.left,cy-a.top);
    ctx.fillStyle='#d2992210';ctx.fillRect(cx,cy,a.right-cx,a.bottom-cy);
    ctx.fillStyle='#f8514910';ctx.fillRect(a.left,cy,cx-a.left,a.bottom-cy);
    ctx.strokeStyle='#2d333b';ctx.beginPath();ctx.moveTo(cx,a.top);ctx.lineTo(cx,a.bottom);ctx.moveTo(a.left,cy);ctx.lineTo(a.right,cy);ctx.stroke();
    ctx.fillStyle='#8b949e';ctx.font='11px sans-serif';
    ctx.fillText('IMPROVING',a.left+6,a.top+14);ctx.fillText('LEADING',a.right-64,a.top+14);
    ctx.fillText('LAGGING',a.left+6,a.bottom-6);ctx.fillText('WEAKENING',a.right-76,a.bottom-6);ctx.restore();}}]});
  // label points
}
document.querySelectorAll('#rrgTabs button').forEach(b=>b.onclick=()=>{document.querySelectorAll('#rrgTabs button').forEach(x=>x.classList.remove('on'));b.classList.add('on');drawRRG(b.dataset.f)});
drawRRG('theme');

// ---- Heatmap ----
function cellColor(v){ if(v===null||isNaN(v)) return 'transparent';
  const a=Math.min(Math.abs(v)/12,1)*.75+.08; return v>=0?'rgba(46,160,67,'+a+')':'rgba(248,81,73,'+a+')';}
function drawHM(sortKey){
  const t=document.getElementById('hmT');
  const rows=[...names].sort((a,b)=>M.themes[b][sortKey]-M.themes[a][sortKey]);
  let h='<tr><th>ธีม / Sector</th><th>1D%</th><th>1W%</th><th>1M%</th><th>3M%</th><th>1M vs SPY</th></tr>';
  rows.forEach(n=>{const d=M.themes[n];
    h+='<tr><td class="name">'+n+'<span class="badge q-'+d.quad+'">'+d.quad+'</span></td>';
    ['r1d','r1w','r1m','r3m','rel1m'].forEach(k=>{h+='<td style="background:'+cellColor(d[k])+'">'+(d[k]>0?'+':'')+d[k].toFixed(2)+'</td>'});
    h+='</tr>'});
  t.innerHTML=h;}
document.querySelectorAll('#hmTabs button').forEach(b=>b.onclick=()=>{document.querySelectorAll('#hmTabs button').forEach(x=>x.classList.remove('on'));b.classList.add('on');drawHM(b.dataset.k)});
drawHM('r1m');

// ---- Breadth ----
(function(){const t=document.getElementById('brT');
 const rows=Object.keys(M.breadth).sort((a,b)=>M.breadth[b].pct_above_20dma-M.breadth[a].pct_above_20dma);
 let h='<tr><th>ธีม</th><th style="width:38%">% สมาชิกเหนือ 20DMA</th><th>Dollar Vol Ratio (5D/20D)</th></tr>';
 rows.forEach(n=>{const d=M.breadth[n];const c=d.pct_above_20dma>=60?'#3fb950':d.pct_above_20dma>=35?'#d29922':'#f85149';
  h+='<tr><td class="name">'+n+'</td><td><div class="bcell"><div class="bar"><i style="width:'+d.pct_above_20dma+'%;background:'+c+'"></i></div><span style="color:'+c+'">'+d.pct_above_20dma+'%</span></div></td>';
  const vc=d.dollar_vol_ratio>=1.05?'#3fb950':d.dollar_vol_ratio<=0.9?'#f85149':'#8b949e';
  h+='<td style="color:'+vc+'">'+d.dollar_vol_ratio.toFixed(2)+'×</td></tr>'});
 t.innerHTML=h;})();

// ---- Playbook ----
(function(){
 function bOf(n){return M.breadth[n]||null}
 function chip(n){const d=M.themes[n];const b=bOf(n);
  let cls='chip-etf', btxt='ETF';
  if(b){const p=b.pct_above_20dma;
   cls = p>=50?'chip-good':p>=30?'chip-mid':'chip-bad';
   btxt = 'B '+p+'%';}
  return '<span class="chip '+cls+'"><b>'+n+'</b> '+(d.rel1m>0?'+':'')+d.rel1m.toFixed(1)+'% <i>'+btxt+'</i></span>';}
 function render(list){return list.map(chip).join('')||'<span class="chip chip-etf">— ไม่มี —</span>'}
 ['Leading','Improving','Weakening','Lagging'].forEach(q=>{
  const el=document.getElementById('q-'+q);
  const list=names.filter(n=>M.themes[n].quad===q).sort((a,b)=>M.themes[b].rel1m-M.themes[a].rel1m);
  if(q==='Improving'){
   const good=list.filter(n=>bOf(n)&&bOf(n).pct_above_20dma>=50);
   const risky=list.filter(n=>bOf(n)&&bOf(n).pct_above_20dma<50);
   const etf=list.filter(n=>!bOf(n));
   el.innerHTML='<div class="sub" style="color:var(--green)">✅ breadth ฟื้นแล้ว — เข้าเกณฑ์น่าจับตา</div>'+render(good)
    +'<div class="sub" style="color:var(--red)">⚠️ breadth ยังเสี่ยง — แค่ลงช้ากว่าตลาด อย่าเพิ่งแตะ</div>'+render(risky)
    +(etf.length?'<div class="sub">Sector ETF (ดู breadth จากธีมย่อยข้างใน)</div>'+render(etf):'');
  } else { el.innerHTML=render(list); }
 });
})();

// ---- Dynamic example (evergreen-safe) ----
(function(){
 const w = names.filter(n=>M.themes[n].quad==='Weakening' && !M.is_sector[n])
   .sort((a,b)=>M.themes[b].r3m-M.themes[a].r3m);
 const el = document.getElementById('dyn-weak');
 if(el && w.length) el.textContent = 'ตัวอย่างรอบนี้: ' + w.slice(0,2).join(', ') + ' (3M ยังบวกแรง แต่โมเมนตัมแผ่วแล้ว)';
})();
</script></body></html>"""

html = html.replace("__DATA__", DATA)

# ---- Appendix: ETF per theme ----
uni = json.load(open(D+"universe.json"))
ETFMAP = {
 "Semiconductors": [("SMH","VanEck Semiconductor"),("SOXX","iShares Semiconductor")],
 "Semi Equip & Memory": [("SMH","น้ำหนัก equipment สูง (ไม่มี ETF เฉพาะกลุ่มนี้ — เน้นเล่นรายตัว)")],
 "Software": [("IGV","iShares Expanded Tech-Software"),("XSW","SPDR S&P Software (equal-weight)")],
 "Mag 7": [("MAGS","Roundhill Magnificent Seven")],
 "Cybersecurity": [("CIBR","First Trust Nasdaq Cybersecurity"),("HACK","Amplify Cybersecurity"),("BUG","Global X Cybersecurity")],
 "Genomics": [("ARKG","ARK Genomic Revolution"),("IDNA","iShares Genomics & Immunology")],
 "Biotech Large": [("IBB","iShares Biotechnology"),("XBI","SPDR S&P Biotech (equal-weight, ตัวเล็กเยอะ)")],
 "Pharma & Managed Care": [("IHE","iShares US Pharmaceuticals"),("XLV","Health Care ทั้ง sector")],
 "Defense": [("ITA","iShares US Aerospace & Defense"),("XAR","SPDR Aerospace & Defense (equal-weight)"),("PPA","Invesco Aerospace & Defense")],
 "Energy": [("XLE","Energy Select Sector"),("XOP","SPDR Oil & Gas E&P (equal-weight)"),("OIH","VanEck Oil Services")],
 "Banks & Brokers": [("KBWB","Invesco KBW Bank"),("KBE","SPDR S&P Bank"),("IAI","iShares US Broker-Dealers")],
 "Staples": [("XLP","Consumer Staples Select Sector")],
 "Utilities & Power": [("XLU","Utilities Select Sector"),("GRID","First Trust Smart Grid Infrastructure")],
 "Materials": [("XLB","Materials Select Sector")],
 "AI Infra & Data Center": [("AIQ","Global X Artificial Intelligence & Technology"),("DTCR","Global X Data Center & Digital Infrastructure"),("GRID","First Trust Smart Grid Infrastructure")],
 "Quantum": [("QTUM","Defiance Quantum")],
 "Nuclear & Uranium": [("URA","Global X Uranium"),("NLR","VanEck Uranium & Nuclear"),("URNM","Sprott Uranium Miners")],
 "Gold Miners": [("GDX","VanEck Gold Miners"),("GDXJ","VanEck Junior Gold Miners"),("GLD","SPDR Gold (ทองคำ spot)")],
 "Solar": [("TAN","Invesco Solar"),("ICLN","iShares Global Clean Energy (กว้างกว่า solar)")],
 "Crypto-linked": [("IBIT","iShares Bitcoin Trust (spot BTC)"),("DAPP","VanEck Digital Transformation"),("WGMI","CoinShares Bitcoin Miners")],
 "Space & Drones": [("ARKX","ARK Space Exploration"),("UFO","Procure Space")],
 "China Tech ADR": [("KWEB","KraneShares CSI China Internet"),("CQQQ","Invesco China Technology")],
 "Homebuilders": [("ITB","iShares US Home Construction"),("XHB","SPDR S&P Homebuilders")],
 "Travel & Airlines": [("JETS","US Global Jets"),("PEJ","Invesco Leisure & Entertainment")],
 "Fintech & Payments": [("IPAY","Amplify Mobile Payments"),("FINX","Global X FinTech")],
}
blocks = ""
for theme, members in uni["baskets"].items():
    etfs = ETFMAP.get(theme, [])
    echips = "".join('<span class="etfc"><b>%s</b> %s</span>' % (t, nm) for t, nm in etfs)
    blocks += ('<div class="apxb"><h4>%s</h4><div>%s</div>'
               '<div class="mem">หุ้นในตะกร้า: %s</div></div>') % (theme, echips, ", ".join(members))
appendix = ('<div class="card full"><h2>📎 Appendix — จะเล่นธีมไหน ไปตัวไหนได้บ้าง</h2>'
 '<div class="apx">' + blocks + '</div>'
 '<div class="note">ข้อควรรู้: ETF ส่วนใหญ่ถ่วงน้ำหนักตาม market cap จึงไม่ตรงกับตะกร้า equal-weight ที่ใช้คำนวณในจอนี้ 100% '
 'ผลตอบแทนอาจต่างกันได้พอสมควรโดยเฉพาะธีมที่มีหุ้นยักษ์ครอบ (เช่น SMH ที่ NVDA กินสัดส่วนสูง) '
 '&bull; เช็คค่าธรรมเนียมและสภาพคล่องก่อนซื้อเสมอ &bull; รายชื่อทั้งหมดคือเครื่องมือประกอบการวิเคราะห์ ไม่ใช่คำแนะนำซื้อขายรายตัวนะคะ</div></div>')
html = html.replace("</div>\n<script>", appendix + "</div>\n<script>")

out = "index.html"
open(out, "w").write(html)
print("written", out, len(html), "bytes")
