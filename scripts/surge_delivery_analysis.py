# -*- coding: utf-8 -*-
"""Copper: price-surge vs delivery-broker OI; delivery-month OI vs warrants/backwardation/premium."""
import json
import numpy as np
import pandas as pd
from scipy import stats

D = '/sessions/optimistic-pensive-archimedes/mnt/outputs/data'
SMELTER = ['金瑞期货', '铜冠金源', '建信期货', '五矿期货']

mt = pd.read_csv(f'{D}/master_totals.csv', dtype={'date': str})
mp = pd.read_csv(f'{D}/master_positions.csv', dtype={'date': str})
prem = pd.read_csv(f'{D}/premium.csv', header=None, names=['date', 'premium'], dtype={0: str})
prem['date'] = pd.to_datetime(prem['date'], format='mixed').dt.strftime('%Y-%m-%d')
prem = prem.set_index('date')['premium']
war = pd.read_csv(f'{D}/warrants_cu.csv', dtype={'date': str}).set_index('date')['tonnes']
sina = pd.read_csv(f'{D}/clean_sina_cu.csv', dtype={'date': str})

cu_t = mt[mt.metal == 'CU'].dropna(subset=['settle'])
# --- main-contract settle series (argmax top-20 volume per date) ---
main = cu_t.loc[cu_t.groupby('date')['volume'].idxmax()][['date', 'contract', 'settle']].set_index('date').sort_index()
px = main['settle']
ret = np.log(px).diff()
# continuity fix: when main contract rolls, use same-contract return
roll = main['contract'] != main['contract'].shift()
ret[roll] = np.nan

# --- front contract per date + smelter front short/long ---
def live(d, cs): return sorted([c for c in cs if c[2:] >= d[2:4] + d[5:7]], key=lambda c: c[2:])
def prompt_ym(d):
    y, mo, day = int(d[:4]), int(d[5:7]), int(d[8:10])
    if day > 15:
        mo += 1
        if mo > 12:
            mo, y = 1, y + 1
    return f'{y % 100:02d}{mo:02d}'
sett_by_d = {d: set(g.contract) for d, g in cu_t.groupby('date')}
# 当月 prompt contract by calendar (16th -> 15th window); absent if unpublished that day.
# Used for coverage / covpath / cycle table. Broker response series use nearest-available (full history).
front = {}
for d, cs in sett_by_d.items():
    pym = prompt_ym(d)
    match = [c for c in cs if c[2:] == pym]
    if match:
        front[d] = match[0]
front_near = {d: live(d, cs)[0] for d, cs in sett_by_d.items() if live(d, cs)}
second = {d: (live(d, cs)[1] if len(live(d, cs)) > 1 else None) for d, cs in sett_by_d.items()}
bwd = pd.Series({d: float(cu_t[(cu_t.date == d) & (cu_t.contract == front[d])].settle.iloc[0] -
                          cu_t[(cu_t.date == d) & (cu_t.contract == second[d])].settle.iloc[0])
                 for d in front if second.get(d) is not None
                 and len(cu_t[(cu_t.date == d) & (cu_t.contract == second[d])])}).sort_index()

cu_p = mp[mp.metal == 'CU'].copy()
cu_p['front'] = cu_p['date'].map(front_near)
fp = cu_p[cu_p.contract == cu_p.front]
sm = fp[fp.member.isin(SMELTER)]
sm_short = sm.groupby('date')['short_oi'].sum().sort_index()
sm_long = sm.groupby('date')['long_oi'].sum().sort_index()
jr = fp[fp.member == '金瑞期货']
jr_short = jr.groupby('date')['short_oi'].sum().sort_index()

# --- surge detection: z-score of daily return vs trailing 15d ---
W = 15
mu = ret.rolling(W).mean().shift(1)
sd = ret.rolling(W).std().shift(1)
z = (ret - mu) / sd
surges = z.dropna()[abs(z.dropna()) >= 2]
print('=== SURGE EVENTS (|z|>=2, %d-day window) ===' % W)
for d, zv in surges.items():
    print(f"{d}  z={zv:+.2f}  ret={ret[d]*100:+.2f}%  px={px[d]:.0f} ({main.loc[d,'contract']})")

# --- event study: smelter front-short change on/after surges ---
dates = sorted(set(sm_short.index) & set(z.dropna().index))
zs = z[dates]
dss = sm_short.reindex(dates)
djr = jr_short.reindex(dates)
def fwd_chg(s, d, k):
    idx = dates.index(d)
    if idx + k >= len(dates): return np.nan
    a, b = s.iloc[idx], s.iloc[idx + k]
    return b - a if pd.notna(a) and pd.notna(b) else np.nan

rows = []
for d in dates:
    if abs(z[d]) >= 2:
        rows.append(dict(date=d, z=z[d], up=z[d] > 0,
                         d0=fwd_chg(dss, d, 1), d3=fwd_chg(dss, d, 3), d5=fwd_chg(dss, d, 5),
                         jr3=fwd_chg(djr, d, 3)))
ev = pd.DataFrame(rows)
print('\n=== Smelter-set front-month SHORT OI change after surges (lots) ===')
if len(ev):
    for lab, g in [('UP surges (price spike)', ev[ev.up]), ('DOWN surges', ev[~ev.up])]:
        if len(g):
            print(f"{lab}: n={len(g)}  T+1 avg {g.d0.mean():+.0f}  T+3 avg {g.d3.mean():+.0f}  T+5 avg {g.d5.mean():+.0f} | Jinrui T+3 {g.jr3.mean():+.0f}")
# regression: daily Δ smelter front short vs z (all days)
dchg = dss.diff().shift(-1)  # next-day change
mask = zs.notna() & dchg.notna()
if mask.sum() > 30:
    slope, icept, r, p, se = stats.linregress(zs[mask], dchg[mask])
    print(f"\nRegression Δ(front short, T+1) = {icept:+.0f} + {slope:+.0f}·z   (r={r:+.2f}, p={p:.3f}, n={mask.sum()})")
    up = zs[mask] > 1
    if up.sum() > 5:
        print(f"When z>+1: avg next-day smelter short change {dchg[mask][up].mean():+.0f} lots (n={up.sum()})")
# unwind into strength: price percentile vs Δshort
pct = px.rank(pct=True).reindex(dates)
mask2 = pct.notna() & dchg.notna()
hi = mask2 & (pct > 0.8)
print(f"Price in top-20% of window: avg daily smelter front-short change {dchg[hi].mean():+.0f} lots (n={hi.sum()}) "
      f"vs all days {dchg[mask2].mean():+.0f}")

# --- delivery coverage: front OI vs warrants (recent cycles) ---
print('\n=== FRONT-MONTH TOP-20 OI vs WARRANTS (coverage), recent cycles ===')
tot_front = cu_t.copy()
tot_front = tot_front[tot_front.apply(lambda r: front.get(r['date']) == r['contract'], axis=1)]
tot_front = tot_front.set_index('date').sort_index()
tot_front['oi_t'] = tot_front[['long_oi', 'short_oi']].max(axis=1) * 5  # lots→tonnes (top-20, kept for cycle table)
# coverage now uses SHFE OFFICIAL per-contract TOTAL OI (kx report) for the calendar prompt contract
toi_df = pd.read_csv(f'{D}/total_oi_cu.csv', dtype={'date': str})
toi_map = {(r.date, r.contract): r.total_oi for r in toi_df.itertuples()}
cov_d, cov_contract = {}, {}
for d in sorted(set(toi_df.date)):
    c = 'CU' + prompt_ym(d)
    if (d, c) in toi_map and d in war.index and war[d] > 0:
        cov_d[d] = toi_map[(d, c)] * 5 / war[d]
        cov_contract[d] = c
cov = pd.Series(cov_d).sort_index()
for d in cov.index[::5]:
    pass
merged = pd.DataFrame({'cov': cov, 'bwd': bwd.reindex(cov.index), 'prem': prem.reindex(cov.index)}).dropna()
if len(merged) > 15:
    print(f"corr(coverage, backwardation) = {merged.cov_col_corr if False else merged['cov'].corr(merged['bwd']):+.2f}   "
          f"corr(coverage, premium) = {merged['cov'].corr(merged['prem']):+.2f}   n={len(merged)}")
print('Latest:', cov.index[-1], f"prompt={cov_contract[cov.index[-1]]}",
      f"total OI(official) vs warrants → ratio {cov.iloc[-1]:.2f}")
print(cov.describe().round(2).to_string())

# --- 23-cycle: pre-delivery front OI (Sina totals) vs premium change into delivery ---
print('\n=== CROSS-CYCLE: pre-delivery front-month OI vs premium behavior ===')
tot_s = sina[(sina.member == 'TOTAL') & (sina.board == 'short')]
rows = []
for contract, g in tot_s.groupby('contract'):
    dm = '20' + contract[2:4] + '-' + contract[4:6]
    pre = g[g.date < dm].sort_values('date')
    if pre.empty: continue
    oi_pre = pre.qty.iloc[-1] * 5  # tonnes
    pdates = [d for d in prem.index if d < dm][-7:]
    idates = [d for d in prem.index if d >= dm][:7]
    if len(pdates) < 5 or len(idates) < 5: continue
    rows.append(dict(cycle=contract, oi_pre_t=oi_pre,
                     prem_pre=prem[pdates].mean(), prem_into=prem[idates].mean(),
                     prem_chg=prem[idates].mean() - prem[pdates].mean(),
                     prem_peak=prem[pdates + idates].max()))
cyc = pd.DataFrame(rows).sort_values('cycle')
print(cyc.to_string(index=False))
if len(cyc) > 8:
    r1, p1 = stats.pearsonr(cyc.oi_pre_t, cyc.prem_chg)
    r2, p2 = stats.pearsonr(cyc.oi_pre_t, cyc.prem_peak)
    print(f"\ncorr(pre-delivery front OI, premium change into delivery) = {r1:+.2f} (p={p1:.3f})")
    print(f"corr(pre-delivery front OI, peak premium around delivery)  = {r2:+.2f} (p={p2:.3f})")
    hi = cyc[cyc.oi_pre_t > cyc.oi_pre_t.quantile(0.75)]
    lo = cyc[cyc.oi_pre_t < cyc.oi_pre_t.quantile(0.25)]
    print(f"High-OI cycles (top quartile): avg prem change {hi.prem_chg.mean():+.0f}, peak {hi.prem_peak.mean():.0f}")
    print(f"Low-OI cycles (bottom quartile): avg prem change {lo.prem_chg.mean():+.0f}, peak {lo.prem_peak.mean():.0f}")

# save outputs for dashboard (with realized smelter-short response per event, filled as days pass)
def ev_payload(d, zv):
    p = {'date': d, 'z': round(float(zv), 2), 'ret': round(float(ret[d]) * 100, 2), 'px': float(px[d])}
    if d in dates:
        for k, key in [(1, 'd1'), (3, 'd3'), (5, 'd5')]:
            v = fwd_chg(dss, d, k)
            if pd.notna(v): p[key] = int(v)
        vj = fwd_chg(djr, d, 3)
        if pd.notna(vj): p['jr3'] = int(vj)
    return p

surge_list = [ev_payload(d, zv) for d, zv in surges.items()]
# active surge watch: latest surge within the last 5 trading days
watch = None
if len(surges):
    last_sd = surges.index[-1]
    if last_sd in dates:
        k = len(dates) - 1 - dates.index(last_sd)
        if 0 < k <= 5:
            delta = sm_short.reindex(dates).iloc[-1] - sm_short.reindex(dates).loc[last_sd]
            watch = {'date': last_sd, 'z': round(float(surges[last_sd]), 2),
                     'days': int(k), 'chg': int(delta) if pd.notna(delta) else None}
# --- price acceptance: smelter TOTAL short book response by price level ---
sm_all = mp[(mp.metal == 'CU') & (mp.member.isin(SMELTER))]
tot_short = sm_all.groupby('date')['short_oi'].sum().sort_index()
common_d = sorted(set(tot_short.index) & set(px.index))
ts_ = tot_short.reindex(common_d)
px_ = px.reindex(common_d)
pctl = px_.rolling(60, min_periods=20).rank(pct=True)
dsh = ts_.diff().shift(-1)  # next-day change in total smelter short
acc = pd.DataFrame({'pct': pctl, 'dsh': dsh}).dropna()
buckets = [(0, .2), (.2, .4), (.4, .6), (.6, .8), (.8, 1.01)]
accept = []
acc_recent = acc.iloc[-21:]          # ~this month
acc_prior = acc.iloc[-84:-21]        # ~prior 3 months
print('\n=== PRICE ACCEPTANCE: avg next-day Δ smelter TOTAL short, this month vs prior 3 months ===')
for lo, hi in buckets:
    gr = acc_recent[(acc_recent.pct >= lo) & (acc_recent.pct < hi)]
    gp = acc_prior[(acc_prior.pct >= lo) & (acc_prior.pct < hi)]
    vr = gr.dsh.mean() if len(gr) >= 3 else np.nan
    vp = gp.dsh.mean() if len(gp) >= 3 else np.nan
    accept.append({'b': f'{int(lo*100)}-{int(hi*100 if hi<=1 else 100)}%',
                   'recent': round(float(vr)) if pd.notna(vr) else None, 'nr': len(gr),
                   'prior': round(float(vp)) if pd.notna(vp) else None, 'np': len(gp)})
    print(f"  {int(lo*100)}-{int(min(hi,1)*100)}%: this month {vr if pd.notna(vr) else '—'} (n={len(gr)}) | prior 3m {vp if pd.notna(vp) else '—'} (n={len(gp)})")

# --- unwind pace: current cycle vs historical average path (normalized smelter front short) ---
# historical: Sina archive, smelter members' short board qty on the front contract, ~6 obs per cycle
sn_sm = sina[(sina.board == 'short') & (sina.member.isin(SMELTER + ['国投安信', '申银万国']))]
sn_sm = sina[(sina.board == 'short') & (sina.member.isin(SMELTER))]
TAGS = ['P-3', 'P-2', 'P-1', 'I+1', 'I+2', 'I+3']
hist_curves = []
for contract, g in sn_sm.groupby('contract'):
    dm = '20' + contract[2:4] + '-' + contract[4:6]
    daily = g.groupby('date')['qty'].sum().sort_index()
    pre = daily[daily.index < dm].iloc[-3:]
    into = daily[daily.index >= dm].iloc[:3]
    if len(pre) < 3 or len(into) < 2:
        continue
    base = pre.iloc[0]
    if not base or base < 500:
        continue
    vals = list(pre.values) + list(into.values) + [np.nan] * (3 - len(into))
    hist_curves.append([v / base if pd.notna(v) else np.nan for v in vals])
hist = np.nanmean(np.array(hist_curves, dtype=float), axis=0) if hist_curves else []
print('\n=== UNWIND PACE: historical avg normalized smelter front-short path (base=P-3) ===')
print('  ', {t: round(float(v), 3) for t, v in zip(TAGS, hist)}, f'(n={len(hist_curves)} cycles)')

# current cycle: smelter front short (EM daily), last 6 sessions mapped onto same axis
cur_short = sm_short.dropna().sort_index()
cur6 = cur_short.iloc[-6:]
cur_base = cur6.iloc[0] if len(cur6) else np.nan
cur_norm = [round(float(v / cur_base), 3) for v in cur6.values] if cur_base else []
pace_cur = (cur6.iloc[-1] / cur6.iloc[0]) ** (1 / max(len(cur6) - 1, 1)) - 1 if len(cur6) > 1 and cur6.iloc[0] else np.nan
pace_hist = (hist[2] / hist[0]) ** (1 / 2) - 1 if len(hist) > 2 and hist[0] else np.nan
print(f'  current cycle last-6-session path: {cur_norm} | pace {pace_cur*100:+.1f}%/session vs hist pre-delivery {pace_hist*100:+.1f}%/session')

# --- coverage path: current cycle vs previous cycles' average, aligned by sessions-to-delivery ---
cov_df = pd.DataFrame({'cov': cov, 'contract': pd.Series(cov_contract).reindex(cov.index)}).dropna()
NPRE, NINTO = 12, 8
ctags = [f'P-{i}' for i in range(NPRE, 0, -1)] + [f'I+{i}' for i in range(1, NINTO + 1)]
paths = {}
for contract, g in cov_df.groupby('contract'):
    dm = '20' + contract[2:4] + '-' + contract[4:6]
    g = g.sort_index()
    pre = g[g.index < dm].iloc[-NPRE:]
    into = g[g.index >= dm].iloc[:NINTO]
    vals = [np.nan] * (NPRE - len(pre)) + list(pre['cov']) + list(into['cov']) + [np.nan] * (NINTO - len(into))
    paths[contract] = (vals, list(pre.index) + list(into.index))
cur_contract = cov_df['contract'].iloc[-1]
hist_mat = [v for c, (v, _) in paths.items() if c != cur_contract]
cov_hist = np.nanmean(np.array(hist_mat, dtype=float), axis=0) if hist_mat else []
cur_vals, cur_dates2 = paths.get(cur_contract, ([], []))
# align current (may be partial: still pre-delivery) — pad so its last obs sits at correct tag
n_into_cur = sum(1 for d in cur_dates2 if d >= '20' + cur_contract[2:4] + '-' + cur_contract[4:6])
# surge flags on current window
surge_map = {d: float(zv) for d, zv in surges.items()}
pad = [np.nan] * (NPRE - (len(cur_dates2) - n_into_cur))
cur_dates_padded = [None] * len(pad) + cur_dates2
cur_flags = [surge_map.get(d) if d else None for d in cur_dates_padded][:len(ctags)]
print('\n=== COVERAGE PATH: current %s vs prev-cycle avg (n=%d) ===' % (cur_contract, len(hist_mat)))
print('  hist:', [round(float(v), 1) if pd.notna(v) else None for v in cov_hist])
print('  cur :', [round(float(v), 1) if pd.notna(v) else None for v in cur_vals])

# --- monthly delivery-cycle table: front-contract top-20 L/S per cycle window ---
tf2 = tot_front.reset_index()  # date, contract, volume, long_oi, short_oi, settle, oi_t
cyc_rows = []
for contract, g in tf2.groupby('contract'):
    # true 当月 window: 16th of month before delivery -> 15th of delivery month
    y, m = 2000 + int(contract[2:4]), int(contract[4:6])
    pm_y, pm_m = (y, m - 1) if m > 1 else (y - 1, 12)
    wstart = f'{pm_y:04d}-{pm_m:02d}-16'
    wend = f'{y:04d}-{m:02d}-15'
    g = g[(g.date >= wstart) & (g.date <= wend)].sort_values('date')
    if len(g) < 5:
        continue
    prem_win = prem.reindex(g.date).dropna()
    # residual (small members + non-members) if total-OI feed exists
    resid_l = resid_s = None
    try:
        toi = pd.read_csv(f'{D}/total_oi_cu.csv', dtype={'date': str})
        toi = toi[toi.contract == contract].set_index('date')['total_oi'].reindex(g.date)
        resid_l = float((toi.values - g.long_oi.values).mean())
        resid_s = float((toi.values - g.short_oi.values).mean())
    except Exception:
        pass
    cyc_rows.append(dict(cycle=contract, days=len(g),
                         start=g.date.iloc[0], end=g.date.iloc[-1],
                         avg_long=round(g.long_oi.mean()), avg_short=round(g.short_oi.mean()),
                         peak_long=int(g.long_oi.max()), peak_short=int(g.short_oi.max()),
                         sl_ratio=round(g.short_oi.mean() / g.long_oi.mean(), 2) if g.long_oi.mean() else None,
                         avg_prem=round(prem_win.mean()) if len(prem_win) else None,
                         resid_long=round(resid_l) if resid_l is not None else None,
                         resid_short=round(resid_s) if resid_s is not None else None))
cyc_tbl = pd.DataFrame(cyc_rows).sort_values('cycle')
if len(cyc_tbl) > 1:
    histm = cyc_tbl.iloc[:-1]
    cur = cyc_tbl.iloc[-1]
    print('\n=== MONTHLY CYCLE TABLE (front-contract top-20) ===')
    print(cyc_tbl.to_string(index=False))
    print(f"Current {cur.cycle}: avg L {cur.avg_long} vs hist avg {histm.avg_long.mean():.0f} ({(cur.avg_long/histm.avg_long.mean()-1)*100:+.0f}%), "
          f"avg S {cur.avg_short} vs {histm.avg_short.mean():.0f} ({(cur.avg_short/histm.avg_short.mean()-1)*100:+.0f}%)")

# --- residual OI (总持仓 − 前20): per-day, prompt contract, aligned by cycle for comparison ---
resid = {}
try:
    toi = pd.read_csv(f'{D}/total_oi_cu.csv', dtype={'date': str})
    toi_map = {(r.date, r.contract): r.total_oi for r in toi.itertuples()}
    rr = []
    for r in tf2.itertuples():
        key = (r.date, r.contract)
        if r.contract[2:] != prompt_ym(r.date) or key not in toi_map:
            continue
        tot_i = toi_map[key]
        rr.append(dict(date=r.date, contract=r.contract, total=int(tot_i),
                       rl=int(tot_i - r.long_oi), rs=int(tot_i - r.short_oi),
                       shareL=round(r.long_oi / tot_i, 3), shareS=round(r.short_oi / tot_i, 3)))
    rdf = pd.DataFrame(rr).sort_values('date')
    cyc_paths = {}
    for contract, g in rdf.groupby('contract'):
        y, mth = 2000 + int(contract[2:4]), int(contract[4:6])
        dm = f'{y:04d}-{mth:02d}'
        pre = g[g.date < dm].iloc[-NPRE:]
        into = g[g.date >= dm].iloc[:NINTO]
        def padvals(col):
            v = [None] * (NPRE - len(pre)) + [int(x) for x in pre[col]] + [int(x) for x in into[col]] + [None] * (NINTO - len(into))
            return v
        cyc_paths[contract] = {'rl': padvals('rl'), 'rs': padvals('rs')}
    # add earlier cycles (CU2606/07) via Sina archive top-20 totals + kx total OI (sparse: P-3..I+3)
    have = set(cyc_paths.keys())
    tot_l = sina[(sina.member == 'TOTAL') & (sina.board == 'long')].set_index(['contract', 'date'])['qty']
    tot_s = sina[(sina.member == 'TOTAL') & (sina.board == 'short')].set_index(['contract', 'date'])['qty']
    for contract in ['CU2606', 'CU2607']:
        if contract in have:
            continue
        y, mth = 2000 + int(contract[2:4]), int(contract[4:6])
        dm = f'{y:04d}-{mth:02d}'
        rows2 = []
        for (c, d), ql in tot_l.items():
            if c != contract or (d, c) not in toi_map or c[2:] != prompt_ym(d):
                continue
            qs = tot_s.get((c, d))
            if qs is None:
                continue
            t = toi_map[(d, c)]
            rows2.append(dict(date=d, rl=int(t - ql), rs=int(t - qs)))
        if len(rows2) < 4:
            continue
        g2 = pd.DataFrame(rows2).sort_values('date')
        pre2 = g2[g2.date < dm].iloc[-NPRE:]
        into2 = g2[g2.date >= dm].iloc[:NINTO]
        def pv(col):
            return [None] * (NPRE - len(pre2)) + [int(x) for x in pre2[col]] + [int(x) for x in into2[col]] + [None] * (NINTO - len(into2))
        cyc_paths[contract] = {'rl': pv('rl'), 'rs': pv('rs')}
    # 3-month-before average (all cycles except the current/latest)
    cn = sorted(cyc_paths.keys())
    curc = cn[-1]
    histc = cn[:-1][-3:]
    def avg_path(key):
        arrs = [np.array([np.nan if v is None else v for v in cyc_paths[c][key]], dtype=float) for c in histc]
        if not arrs:
            return []
        m = np.nanmean(np.vstack(arrs), axis=0)
        return [round(float(v)) if not np.isnan(v) else None for v in m]
    avg3 = {'rl': avg_path('rl'), 'rs': avg_path('rs'), 'n': len(histc), 'cycles': histc}
    print('  3m-before avg from cycles:', histc)

    r63 = rr[-63:]  # ≤3-month window for the average
    resid = {'tags': ctags, 'cycles': cyc_paths, 'avg3': avg3,
             'series': {r['date']: [r['rl'], r['rs'], r['total']] for r in rr},
             'avgL': round(float(np.mean([x['rl'] for x in r63]))) if r63 else None,
             'avgS': round(float(np.mean([x['rs'] for x in r63]))) if r63 else None,
             'latest': rr[-1] if rr else None}
    print('\n=== RESIDUAL OI (total − top20), prompt contract ===')
    for x in rr[-5:]:
        print(f"  {x['date']} {x['contract']}: total {x['total']}, resid L {x['rl']} ({(1-x['shareL'])*100:.0f}%), resid S {x['rs']} ({(1-x['shareS'])*100:.0f}%)")
except Exception as e:
    print('residual skipped:', e)

out = {'surges': surge_list, 'watch': watch, 'accept': accept, 'resid': resid,
       'cycles_tbl': cyc_tbl.where(pd.notna(cyc_tbl), None).to_dict(orient='records'),
       'covpath': {'tags': ctags,
                   'hist': [round(float(v), 2) if pd.notna(v) else None for v in cov_hist],
                   'cur': [round(float(v), 2) if pd.notna(v) else None for v in cur_vals],
                   'cur_flags': cur_flags, 'cur_contract': cur_contract,
                   'ncycles': len(hist_mat)},
       'pace': {'tags': TAGS, 'hist': [round(float(v), 3) if pd.notna(v) else None for v in hist],
                'cur': cur_norm, 'cur_dates': list(cur6.index),
                'cur_pace': round(float(pace_cur) * 100, 1) if pd.notna(pace_cur) else None,
                'hist_pace': round(float(pace_hist) * 100, 1) if pd.notna(pace_hist) else None,
                'ncycles': len(hist_curves)},
       'px': {d: float(v) for d, v in px.items()},
       'sm_short': {d: int(v) for d, v in sm_short.dropna().items()},
       'sm_long': {d: int(v) for d, v in sm_long.dropna().items()},
       'coverage': {d: round(float(v), 2) for d, v in cov.items()},
       'warrants': {d: float(v) for d, v in war.items()},
       'cycles': cyc.round(1).to_dict(orient='records')}
json.dump(out, open(f'{D}/surge_delivery.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('\nsaved surge_delivery.json')
