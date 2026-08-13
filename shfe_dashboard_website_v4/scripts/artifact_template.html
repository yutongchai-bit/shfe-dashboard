<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>SHFE Broker OI vs Physical Premium — Live</title>
<script src="vendor/chart.umd.js"></script>
<script src="vendor/gridjs.umd.js"></script>
<link rel="stylesheet" href="vendor/gridjs.css">
<style>
  :root { color-scheme: light; }
  body { margin:0; background:#f6f8fb; color:#1c2733; font:13.5px/1.5 'Segoe UI',Arial,sans-serif; }
  header { padding:16px 24px 4px; }
  h1 { font-size:18px; margin:0 0 4px; }
  .sub { color:#5a6b7f; font-size:12px; max-width:1100px; }
  .controls { display:flex; gap:12px; padding:10px 24px; flex-wrap:wrap; align-items:center; }
  select,button,input { background:#fff; color:#1c2733; border:1px solid #c9d4e0; border-radius:6px; padding:6px 10px; font-size:13px; }
  button { cursor:pointer; }
  .card { background:#fff; border:1px solid #e3e9f0; border-radius:10px; padding:12px 14px; margin:0 24px 14px; }
  .grid2 { display:grid; grid-template-columns:1fr 1fr; gap:14px; margin:0 24px 14px; }
  .grid2 .card { margin:0; }
  @media (max-width:1100px){ .grid2 { grid-template-columns:1fr; } }
  .card h3 { margin:2px 0 8px; font-size:14px; }
  .chartbox { position:relative; height:300px; }
  .chartbox2 { position:relative; height:360px; }
  .kpis { display:flex; gap:12px; flex-wrap:wrap; padding:2px 24px 10px; }
  .kpi { background:#fff; border:1px solid #e3e9f0; border-radius:10px; padding:8px 16px; min-width:140px; }
  .kpi .v { font-size:19px; font-weight:700; }
  .kpi .l { color:#5a6b7f; font-size:11px; }
  .status { font-size:11.5px; color:#5a6b7f; padding:0 24px 8px; }
  .status .ok { color:#1b7f3b; } .status .err { color:#b3261e; }
  .note { color:#5a6b7f; font-size:11px; margin-top:6px; }
  .warn { color:#9a6b00; font-size:11.5px; margin:2px 0 6px; }
  .pill { display:inline-block; padding:1px 8px; border-radius:10px; font-size:11px; background:#e8eef6; }
  .bset { display:flex; flex-wrap:wrap; gap:8px 14px; align-items:center; }
  .bset label { display:flex; align-items:center; gap:4px; background:#f2f6fa; border:1px solid #dbe4ee; border-radius:6px; padding:3px 8px; font-size:12.5px; }
  .bset label.sm { background:#fdeeea; border-color:#f3c9bf; }
  .gridjs-wrapper { box-shadow:none; }
</style>
</head>
<body>
<header>
  <h1>SHFE Broker Positioning vs Physical Premium — Live</h1>
  <div class="sub">Daily SHFE top-20 member rankings (via EastMoney mirror). <b>Backwardation</b> = front-month − 2nd-month
  settlement spread (¥/t, always available, a physical-tightness proxy). <b>Premium</b> = your own physical premium series
  (e.g. SMM Yangshan / domestic spot premium) uploaded as CSV — stored on this device. Broker books mix house and client flow —
  smelter attribution (Jinrui→JCC, 铜冠金源→Tongling, 中金岭南→zinc) is market convention, not disclosure.</div>
</header>
<div class="controls">
  <label>Metal <select id="metal"><option>CU</option><option>AL</option><option>ZN</option></select></label>
  <label>Period <select id="period">
    <option value="all">All available</option>
    <option value="6m">Last 6 months</option>
    <option value="3m" selected>Last 3 months</option>
    <option value="1m">Last month</option>
    <option value="2w">Last 2 weeks</option>
  </select></label>
  <label>L/S scope <select id="lsscope"></select></label>
  <label>Premium CSV (date,premium) <input type="file" id="csv" accept=".csv"></label>
  <button id="clearovr" style="display:none">Clear premium</button>
  <span id="ovr" class="pill">premium: not loaded</span>
</div>
<div class="status" id="status">Loading…</div>
<div class="kpis" id="kpis"></div>
<div class="card"><h3 id="tb">Front-month position ranking</h3>
  <div class="grid2" style="margin:0;grid-template-columns:1fr 1fr;gap:14px">
    <div><div class="note" style="margin:0 0 4px"><b>Long board</b></div><div id="gb1"></div></div>
    <div><div class="note" style="margin:0 0 4px"><b>Short board</b></div><div id="gb2"></div></div>
  </div>
  <div class="note">Full SHFE top-20 boards for the front-month contract, latest session (all members, not just tracked ones).
  Refreshed nightly.</div></div>
<div class="card"><h3>Smelter-related broker set <span class="pill" style="margin-left:6px">your tags, saved locally</span></h3>
  <div class="bset" id="bset"></div>
  <div style="margin-top:8px"><button id="selproven">Select brokers with delivery track record (≥3 cycles)</button></div>
  <div class="note"><b>How the default set was chosen:</b> corporate affiliation — 金瑞期货 is Jiangxi Copper's broker, 铜冠金源 is
  Tongling Nonferrous', 中金岭南 is a zinc smelter affiliate, 五矿期货 is Minmetals group — plus 建信期货, included not by ownership
  but because its book shows a persistent producer-style short position with a recurring delivery signature (likely smelter client
  flow routed through a bank broker). This is convention/inference, not disclosure. For a purely data-driven set, use the button
  above: it tags every tracked broker that carried material short OI (≥300 lots) into the delivery month in at least 3 of the 23
  copper delivery cycles sampled (Sep 2024 – Jul 2026). The full track record table is below.</div>
  <div id="gdr" style="margin-top:10px"></div>
  <div class="note">Delivery track record (copper): cycles = delivery months where the member sat on the front-month short board
  with ≥300 lots inside the delivery month; avg/max lots and avg share of the top-20 short board measured on those occasions.
  Caveat: top-20 short OI held into delivery signals delivery <i>capacity/intent</i>, not confirmed delivered volume, and client
  flow at big brokers (中信, 国泰君安) also shows up here.</div></div>
<div class="grid2">
  <div class="card"><h3 id="t1">1 — Front-month net OI vs Premium</h3><div id="w1" class="warn" style="display:none"></div>
    <div class="chartbox"><canvas id="c1"></canvas></div>
    <div class="note">Smelter-tagged brokers, net OI (long − short) on the front-month contract; premium on the right axis.</div></div>
  <div class="card"><h3 id="t2">2 — Front-month net OI vs Backwardation</h3>
    <div class="chartbox"><canvas id="c2"></canvas></div>
    <div class="note">Same positions against the F1−F2 settlement backwardation (¥/t).</div></div>
  <div class="card"><h3 id="t3">3 — Front-month long &amp; short OI vs Premium</h3><div id="w3" class="warn" style="display:none"></div>
    <div class="chartbox"><canvas id="c3"></canvas></div>
    <div class="note">Long (green) and short (red) OI on the front month for the scope chosen above; premium on the right axis.
    A short book held up while premium rises = delivery-hedge signature.</div></div>
  <div class="card"><h3 id="t4">4 — Front-month long &amp; short OI vs Backwardation</h3>
    <div class="chartbox"><canvas id="c4"></canvas></div>
    <div class="note">Same long/short positions against backwardation.</div></div>
</div>
<div class="card"><h3 id="t7">Front-month top-20: total shorts − total longs</h3><div id="w7" class="warn" style="display:none"></div>
  <div class="chartbox2"><canvas id="c7"></canvas></div>
  <div class="note">Bars = top-20 short-board sum − top-20 long-board sum on the front-month contract (positive = the biggest
  shorts out-size the biggest longs → short-side concentration into delivery). Thin lines = the underlying top-20 long and short
  totals. Right axis: backwardation (orange) and premium (purple, when loaded).</div>
  <div id="g4" style="margin-top:10px"></div></div>
<div class="card"><h3 id="t6">Total net OI vs Premium &amp; Backwardation</h3><div id="w6" class="warn" style="display:none"></div>
  <div class="chartbox2"><canvas id="c6"></canvas></div>
  <div class="note">Blue = market-wide top-20 net OI (sum of all long boards − all short boards, every contract): positive means
  the biggest longs out-size the biggest shorts. Teal = net OI summed over your tracked brokers only. Right axis: backwardation
  (orange dashed) and your premium series (purple dashed, when loaded).</div></div>
<div class="card"><h3 id="t5">All tracked brokers — cumulative net-OI change vs backwardation change</h3>
  <div class="chartbox2"><canvas id="c5"></canvas></div>
  <div class="note">Each line = cumulative change in broker net OI (all contracts, lots) since first shown date; orange dashed =
  cumulative backwardation change (¥/t, right axis). Click legend entries to hide/show.</div></div>
<div class="card"><h3>Broker statistics (computed for the selected period)</h3><div id="g1"></div>
  <div class="note">corr(level)/corr(Δ): broker all-contract net OI vs backwardation (levels / daily changes); front-corr: front-month
  net OI vs backwardation; prem-corr: front-month net OI vs your premium series (— until uploaded); best lag: shift of broker series
  maximising |r| in −10..+10 trading days (positive = broker leads). SM = tagged smelter-related.</div></div>
<div class="card"><h3>Full daily data — all contracts net OI</h3><div id="g2"></div>
  <div class="note">Net OI per broker across all contracts (blank-as-zero when off a top-20 board). Sortable; latest first.</div></div>
<div class="card"><h3>Full daily data — front-month positions</h3><div id="g3"></div>
  <div class="note">Front-month net OI per broker, plus long/short detail for the L/S scope selection. Latest first.</div></div>
<script>
/*__BASELINE__*/
const DELIV_DEFAULT = {CU:['金瑞期货','铜冠金源','建信期货','五矿期货'], AL:['金瑞期货','铜冠金源','建信期货','五矿期货'], ZN:['金瑞期货','铜冠金源','建信期货','五矿期货','中金岭南']};
const PALETTE = ['#1f77b4','#d62728','#2ca02c','#9467bd','#8c564b','#e377c2','#17a2b8','#bcbd22','#ff7f0e','#7f7f7f','#3949ab','#00897b','#c62828','#6d4c41'];
const SETSUM = '__SET__';
const $ = id => document.getElementById(id);
const state = { metal:'CU', period: localStorage.getItem('shfe_period')||'3m', ls: SETSUM };
let charts = {}, grids = {};
let userPremium = JSON.parse(localStorage.getItem('shfe_prem_ovr')||'null');
const lsGet = (k,d) => { try{ return JSON.parse(localStorage.getItem(k)) ?? d; }catch(e){ return d; } };

function smelterSet(metal){
  const saved = lsGet('shfe_smelter_set', {});
  return saved[metal] || DELIV_DEFAULT[metal] || [];
}
function setSmelter(metal, arr){
  const saved = lsGet('shfe_smelter_set', {});
  saved[metal] = arr; localStorage.setItem('shfe_smelter_set', JSON.stringify(saved));
}
function seriesFor(metal){
  const st = BASELINE.metals[metal];
  const brokers = {};
  for(const b in st.brokers){
    const B = st.brokers[b];
    const net = {}, fnet = {};
    for(const d of new Set([...Object.keys(B.long||{}),...Object.keys(B.short||{})])) net[d] = ((B.long||{})[d]||0)-((B.short||{})[d]||0);
    for(const d of new Set([...Object.keys(B.nlong||{}),...Object.keys(B.nshort||{})])) fnet[d] = ((B.nlong||{})[d]||0)-((B.nshort||{})[d]||0);
    if(Object.keys(net).length) brokers[b] = {net, fnet, flong:B.nlong||{}, fshort:B.nshort||{}};
  }
  const totNet = {};
  for(const d in (st.tot||{})) totNet[d] = st.tot[d][0] - st.tot[d][1];
  return {bwd: st.spread, brokers, totNet, ftot: st.ftot||{}};
}
function pearson(xs,ys){ const n=xs.length; if(n<10) return null;
  const mx=xs.reduce((a,b)=>a+b,0)/n, my=ys.reduce((a,b)=>a+b,0)/n; let sxy=0,sx=0,sy=0;
  for(let i=0;i<n;i++){const a=xs[i]-mx,b=ys[i]-my; sxy+=a*b; sx+=a*a; sy+=b*b;}
  return (sx&&sy)? sxy/Math.sqrt(sx*sy) : null; }
function stats(net, ref){
  const dates = Object.keys(net).filter(d=>ref && d in ref).sort();
  const x = dates.map(d=>net[d]), y = dates.map(d=>ref[d]);
  const lvl = pearson(x,y);
  const dx = x.slice(1).map((v,i)=>v-x[i]), dy = y.slice(1).map((v,i)=>v-y[i]);
  const chg = pearson(dx,dy);
  let best=null;
  for(let lag=-10;lag<=10;lag++){ const xs=[],ys=[];
    for(let i=0;i<dates.length;i++){const j=i-lag; if(j>=0&&j<dates.length){xs.push(x[j]);ys.push(y[i]);}}
    const r=pearson(xs,ys); if(r!==null && (!best||Math.abs(r)>Math.abs(best.r))) best={lag,r}; }
  return {lvl,chg,best,n:dates.length};
}
function sumSeries(list){
  const out={};
  list.forEach(o=>{ for(const d in o) out[d]=(out[d]||0)+o[d]; });
  return out;
}
function renderMgr(brokers){
  const sm = smelterSet(state.metal);
  $('bset').innerHTML = Object.keys(brokers).map(b=>
    `<label class="${sm.includes(b)?'sm':''}"><input type="checkbox" data-b="${b}" ${sm.includes(b)?'checked':''}>${b}</label>`).join('');
  $('bset').querySelectorAll('input[type=checkbox]').forEach(cb=>{
    cb.onchange = ()=>{
      const b = cb.dataset.b; let arr = smelterSet(state.metal).slice();
      if(cb.checked && !arr.includes(b)) arr.push(b);
      if(!cb.checked) arr = arr.filter(x=>x!==b);
      setSmelter(state.metal, arr); render();
    };
  });
}
function mkChart(id,cfg){ if(charts[id]) charts[id].destroy(); charts[id]=new Chart($(id),cfg); }
const ALIAS = {'五矿经易':'五矿期货','国投期货':'国投安信','申万期货':'申银万国'};
function renderBoard(metal){
  const st = BASELINE.metals[metal];
  const b = st.board;
  if(!b){ $('tb').textContent = 'Front-month position ranking — no board data yet'; return; }
  $('tb').textContent = `Front-month position ranking — ${b.contract} (${b.date})`;
  const smNames = new Set(smelterSet(metal));
  const tag = n => smNames.has(ALIAS[n]||n) ? n+' ◆' : n;
  const longs = b.rows.filter(r=>r[1]!=null).sort((a,c)=>a[1]-c[1]).map(r=>[r[1], tag(r[0]), r[2]]);
  const shorts = b.rows.filter(r=>r[3]!=null).sort((a,c)=>a[3]-c[3]).map(r=>[r[3], tag(r[0]), r[4]]);
  const style = {td:{padding:'3px 8px',fontSize:'12px'},th:{padding:'5px 8px',fontSize:'11.5px'}};
  $('gb1').innerHTML=''; new gridjs.Grid({columns:['#','Broker','Long OI'], data:longs, style}).render($('gb1'));
  $('gb2').innerHTML=''; new gridjs.Grid({columns:['#','Broker','Short OI'], data:shorts, style}).render($('gb2'));
}
function renderRecord(){
  const rec = BASELINE.delivery_record||[];
  $('gdr').innerHTML='';
  new gridjs.Grid({columns:['Broker','Cycles (of 23)','Avg lots into delivery','Max lots','Avg share of top-20 shorts','Last cycle'],
    data: rec.map(r=>[r.name, r.cycles, r.avg_lots, r.max_lots, (r.avg_share*100).toFixed(1)+'%', r.last]),
    sort:true, pagination:{limit:10}, search:true,
    style:{td:{padding:'4px 8px',fontSize:'12px'},th:{padding:'6px 8px',fontSize:'11.5px'}}}).render($('gdr'));
}
function baseOpts(rightTitle){
  return {responsive:true,maintainAspectRatio:false,interaction:{mode:'index',intersect:false},
    plugins:{legend:{labels:{boxWidth:12,font:{size:11}}}},
    scales:{y:{title:{display:true,text:'lots'}},
            y2:{position:'right',grid:{drawOnChartArea:false},title:{display:true,text:rightTitle}},
            x:{ticks:{maxTicksLimit:10,font:{size:10}}}}};
}
function render(){
  const metal = state.metal;
  const {bwd, brokers, totNet, ftot} = seriesFor(metal);
  const allB = Object.keys(brokers);
  const sm = smelterSet(metal).filter(b=>allB.includes(b));
  // axis with period filter
  const all = new Set(Object.keys(bwd)); allB.forEach(b=>Object.keys(brokers[b].net).forEach(d=>all.add(d)));
  let axis = [...all].sort();
  if(state.period !== 'all' && axis.length){
    const months = {'6m':6,'3m':3,'1m':1}[state.period];
    const cut = new Date(axis[axis.length-1]);
    if(months) cut.setMonth(cut.getMonth()-months); else cut.setDate(cut.getDate()-14);
    const cutS = cut.toISOString().slice(0,10);
    axis = axis.filter(d=>d>=cutS);
  }
  const inWin = obj => { const o={}; for(const d of axis) if(obj && obj[d]!=null) o[d]=obj[d]; return o; };
  const S = obj => axis.map(d=>(obj&&obj[d])??null);
  const prem = userPremium;
  const premDs = prem ? {label:'premium',data:S(prem),borderColor:'#ff9800',borderDash:[6,4],pointRadius:0,borderWidth:2.5,spanGaps:true,yAxisID:'y2'} : null;
  const bwdDs = {label:'backwardation F1−F2',data:S(bwd),borderColor:'#ff9800',borderDash:[6,4],pointRadius:0,borderWidth:2.5,spanGaps:true,yAxisID:'y2'};
  renderMgr(brokers);
  renderBoard(metal);
  // L/S scope select
  const opts = [[SETSUM,'Smelter set (sum)']].concat(allB.map(b=>[b,b]));
  $('lsscope').innerHTML = opts.map(([v,t])=>`<option value="${v}" ${v===state.ls?'selected':''}>${t}</option>`).join('');
  if(state.ls!==SETSUM && !allB.includes(state.ls)) state.ls = SETSUM;
  const lsName = state.ls===SETSUM ? 'smelter set (sum)' : state.ls;
  const flong = state.ls===SETSUM ? sumSeries(sm.map(b=>inWin(brokers[b].flong))) : inWin(brokers[state.ls].flong);
  const fshort = state.ls===SETSUM ? sumSeries(sm.map(b=>inWin(brokers[b].fshort))) : inWin(brokers[state.ls].fshort);
  const fnetSel = state.ls===SETSUM ? sumSeries(sm.map(b=>inWin(brokers[b].fnet))) : inWin(brokers[state.ls].fnet);
  const smLines = sm.map((b,i)=>({label:b,data:S(brokers[b].fnet),borderColor:PALETTE[i],pointRadius:0,borderWidth:2,spanGaps:true,yAxisID:'y'}));
  // 1 & 2: front net vs premium / backwardation
  const noPrem = !prem;
  $('w1').style.display = noPrem?'':'none';
  $('w1').textContent = 'No premium series loaded — upload your SMM premium CSV (date,premium) in the toolbar to populate the orange line.';
  mkChart('c1',{type:'line',data:{labels:axis,datasets: premDs? [...smLines, premDs] : smLines}, options: baseOpts('premium ¥/t')});
  mkChart('c2',{type:'line',data:{labels:axis,datasets:[...smLines.map(d=>({...d})), bwdDs]}, options: baseOpts('¥/t')});
  // 3 & 4: long/short vs premium / backwardation
  const lsSets = [
    {label:lsName+' long (front)',data:S(flong),borderColor:'#2ca02c',pointRadius:0,borderWidth:2,spanGaps:true,yAxisID:'y'},
    {label:lsName+' short (front)',data:S(fshort),borderColor:'#d62728',pointRadius:0,borderWidth:2,spanGaps:true,yAxisID:'y'},
    {label:lsName+' net (front)',data:S(fnetSel),borderColor:'#1f77b4',borderDash:[3,3],pointRadius:0,borderWidth:1.5,spanGaps:true,yAxisID:'y'}];
  $('w3').style.display = noPrem?'':'none';
  $('w3').textContent = $('w1').textContent;
  mkChart('c3',{type:'line',data:{labels:axis,datasets: premDs? [...lsSets, {...premDs}] : lsSets}, options: baseOpts('premium ¥/t')});
  mkChart('c4',{type:'line',data:{labels:axis,datasets:[...lsSets.map(d=>({...d})), {...bwdDs}]}, options: baseOpts('¥/t')});
  // 7: front-month top-20 shorts - longs
  const fLong={}, fShort={}, fDiff={};
  for(const d in ftot){ fLong[d]=ftot[d][0]; fShort[d]=ftot[d][1]; fDiff[d]=ftot[d][1]-ftot[d][0]; }
  $('w7').style.display = noPrem?'':'none';
  $('w7').textContent = $('w1').textContent;
  const c7sets = [
    {type:'bar',label:'top-20 shorts − longs (front)',data:S(fDiff),backgroundColor:axis.map(d=>(fDiff[d]??0)>=0?'rgba(214,39,40,0.55)':'rgba(44,160,44,0.55)'),yAxisID:'y'},
    {type:'line',label:'top-20 long total (front)',data:S(fLong),borderColor:'#2ca02c',pointRadius:0,borderWidth:1.4,spanGaps:true,yAxisID:'y'},
    {type:'line',label:'top-20 short total (front)',data:S(fShort),borderColor:'#d62728',pointRadius:0,borderWidth:1.4,spanGaps:true,yAxisID:'y'},
    {type:'line',...bwdDs}];
  if(premDs) c7sets.push({type:'line',...premDs, borderColor:'#9467bd', label:'premium'});
  mkChart('c7',{data:{labels:axis,datasets:c7sets}, options: baseOpts('¥/t')});
  // g4: front-month totals table
  const frows = [...axis].reverse().filter(d=>ftot[d]).map(d=>[d, ftot[d][2], ftot[d][0], ftot[d][1], ftot[d][1]-ftot[d][0],
    bwd[d]??'', prem?(prem[d]??''):'']);
  $('g4').innerHTML='';
  grids.g4 = new gridjs.Grid({columns:['Date','Front contract','Top-20 longs','Top-20 shorts','Shorts − longs','Backwd ¥/t','Premium'],
    data:frows, sort:true, pagination:{limit:10},
    style:{td:{padding:'4px 8px',fontSize:'12px'},th:{padding:'6px 8px',fontSize:'11.5px'}}}).render($('g4'));
  // 6: total net OI vs premium & backwardation
  const trackedSum = sumSeries(allB.map(b=>inWin(brokers[b].net)));
  $('w6').style.display = noPrem?'':'none';
  $('w6').textContent = $('w1').textContent;
  const c6sets = [
    {label:'top-20 total net OI',data:S(totNet),borderColor:'#1f77b4',pointRadius:0,borderWidth:2.2,spanGaps:true,yAxisID:'y'},
    {label:'tracked brokers net (sum)',data:S(trackedSum),borderColor:'#17a2b8',borderDash:[3,3],pointRadius:0,borderWidth:1.8,spanGaps:true,yAxisID:'y'},
    {...bwdDs}];
  if(premDs) c6sets.push({...premDs, borderColor:'#9467bd', label:'premium'});
  mkChart('c6',{type:'line',data:{labels:axis,datasets:c6sets}, options: baseOpts('¥/t')});
  // 5: all brokers cumulative
  const toCum = obj => { let base=null; return axis.map(d=>{const v=obj[d]; if(v==null) return null; if(base===null) base=v; return v-base;}); };
  mkChart('c5',{type:'line',data:{labels:axis,datasets:[
    ...allB.map((b,i)=>({label:b,data:toCum(brokers[b].net),borderColor:PALETTE[i%PALETTE.length],pointRadius:0,borderWidth:1.8,spanGaps:true,yAxisID:'y'})),
    {label:'Δ backwardation',data:toCum(bwd),borderColor:'#ff9800',borderDash:[6,4],pointRadius:0,borderWidth:3,spanGaps:true,yAxisID:'y2'}
  ]},options: baseOpts('Δ ¥/t')});
  // stats grid
  const bwdW = inWin(bwd), premW = prem? inWin(prem) : null;
  const rows = allB.map(b=>{
    const s = stats(inWin(brokers[b].net), bwdW);
    const sf = stats(inWin(brokers[b].fnet), bwdW);
    const sp = premW? stats(inWin(brokers[b].fnet), premW) : null;
    const nd = Object.keys(brokers[b].net).sort();
    const last = nd[nd.length-1], v = brokers[b].net[last];
    const d1 = nd.length>1 ? v-brokers[b].net[nd[nd.length-2]] : null;
    const fd = Object.keys(brokers[b].fnet).sort(); const flast = fd[fd.length-1];
    return [sm.includes(b)?'✔':'', b, last, v, d1, flast?brokers[b].fnet[flast]:null,
            s.lvl!=null?+s.lvl.toFixed(3):null, s.chg!=null?+s.chg.toFixed(3):null,
            sf.lvl!=null?+sf.lvl.toFixed(3):null,
            sp&&sp.lvl!=null?+sp.lvl.toFixed(3):'—',
            s.best?`${s.best.lag>0?'+':''}${s.best.lag}d (${s.best.r.toFixed(2)})`:'—', s.n];
  }).sort((a,b)=>a[3]-b[3]);
  $('g1').innerHTML='';
  grids.g1 = new gridjs.Grid({columns:['SM','Broker','As of','Net OI','Δ1d','Front net','corr(level)','corr(Δ)','front-corr','prem-corr','best lag','n'],
    data:rows, sort:true, style:{td:{padding:'5px 9px',fontSize:'12.5px'},th:{padding:'6px 9px',fontSize:'11.5px'}}}).render($('g1'));
  // g2: all-contract daily
  const drows = [...axis].reverse().map(d=>[d, bwd[d]??'', prem?(prem[d]??''):'', ...allB.map(b=>brokers[b].net[d]??'')]);
  $('g2').innerHTML='';
  grids.g2 = new gridjs.Grid({columns:['Date','Backwd ¥/t','Premium',...allB], data:drows, sort:true,
    pagination:{limit:15}, search:true,
    style:{td:{padding:'4px 8px',fontSize:'12px'},th:{padding:'6px 8px',fontSize:'11.5px'}}}).render($('g2'));
  // g3: front-month daily
  const nrows = [...axis].reverse().map(d=>[d, bwd[d]??'', prem?(prem[d]??''):'', flong[d]??'', fshort[d]??'',
    ...allB.map(b=>brokers[b].fnet[d]??'')]);
  $('g3').innerHTML='';
  grids.g3 = new gridjs.Grid({columns:['Date','Backwd ¥/t','Premium',lsName+' long',lsName+' short',...allB.map(b=>b+' front net')],
    data:nrows, sort:true, pagination:{limit:15}, search:true,
    style:{td:{padding:'4px 8px',fontSize:'12px'},th:{padding:'6px 8px',fontSize:'11.5px'}}}).render($('g3'));
  // KPIs
  const bd = Object.keys(bwd).sort(); const lastB = bd[bd.length-1];
  const jr = brokers['金瑞期货']; let jrTxt='—', jrD='';
  if(jr && Object.keys(jr.net).length){ const nd=Object.keys(jr.net).sort(); jrTxt=jr.net[nd[nd.length-1]].toLocaleString(); jrD=nd[nd.length-1]; }
  const fsum = sm.reduce((acc,b)=>{ const k=Object.keys(brokers[b].fnet).sort().pop(); return acc+(k?brokers[b].fnet[k]:0);},0);
  const pd2 = prem? Object.keys(prem).sort() : [];
  $('kpis').innerHTML = [
    ['Backwardation ('+(lastB||'—')+')', bwd[lastB]!=null?bwd[lastB].toLocaleString()+' ¥/t':'—'],
    ['Premium '+(prem?('('+pd2[pd2.length-1]+')'):''), prem? prem[pd2[pd2.length-1]].toLocaleString()+' ¥/t':'not loaded'],
    ['Jinrui net OI ('+jrD+')', jrTxt+' lots'],
    ['Smelter-set front-month net', fsum.toLocaleString()+' lots'],
    ['Days shown', axis.length]
  ].map(([l,v])=>`<div class="kpi"><div class="v">${v}</div><div class="l">${l}</div></div>`).join('');
  ['t1','t2','t3','t4'].forEach((t,i)=>{
    const names = ['Front-month net OI vs Premium','Front-month net OI vs Backwardation',
                   'Front-month long & short OI vs Premium','Front-month long & short OI vs Backwardation'];
    $(t).textContent = (i+1)+' — '+names[i]+' — '+metal;
  });
  $('ovr').textContent = prem ? 'premium: loaded ('+Object.keys(prem).length+' rows)' : 'premium: not loaded';
  $('clearovr').style.display = prem ? '' : 'none';
}
function setStatus(){
  const asof = BASELINE.asof || '—';
  $('status').innerHTML = `<span class="ok">●</span> Data through <b>${asof}</b> — refreshed automatically every weekday evening (18:30) after SHFE publishes daily rankings. Re-open this page to see the latest.`;
}
$('metal').onchange = e=>{ state.metal=e.target.value; render(); };
$('period').onchange = e=>{ state.period=e.target.value; localStorage.setItem('shfe_period',state.period); render(); };
$('lsscope').onchange = e=>{ state.ls=e.target.value; render(); };
$('csv').onchange = e=>{
  const f=e.target.files[0]; if(!f) return;
  const rd=new FileReader();
  rd.onload=()=>{ const m={};
    rd.result.split(/\r?\n/).forEach(line=>{ const p=line.split(',');
      if(p.length>=2 && /^\d{4}-\d{2}-\d{2}$/.test(p[0].trim()) && !isNaN(parseFloat(p[1]))) m[p[0].trim()]=parseFloat(p[1]); });
    if(Object.keys(m).length>5){ userPremium=m; localStorage.setItem('shfe_prem_ovr',JSON.stringify(m)); render(); }
    else alert('Could not parse CSV. Expected rows like: 2026-08-12,55'); };
  rd.readAsText(f);
};
$('clearovr').onclick = ()=>{ userPremium=null; localStorage.removeItem('shfe_prem_ovr'); render(); };
$('selproven').onclick = ()=>{
  const rec = BASELINE.delivery_record||[];
  const proven = new Set(rec.filter(r=>r.cycles>=3).map(r=>r.name));
  const tracked = Object.keys(BASELINE.metals[state.metal].brokers);
  const sel = tracked.filter(b=>proven.has(b)||proven.has(ALIAS[b]||''));
  if(!sel.length){ alert('No tracked broker meets the ≥3-cycle delivery record.'); return; }
  setSmelter(state.metal, sel); render();
};
$('period').value = state.period;
render();
renderRecord();
setStatus();
</script>
</body>
</html>
