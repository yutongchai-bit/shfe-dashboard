# -*- coding: utf-8 -*-
"""Daily refresh pipeline: merge fresh EM pulls into masters, rebuild artifact HTML.

Inputs (written by fetch agents, optional per metal):
  data/fresh_positions_{cu|al|zn}.csv : member,date,contract,long_oi,short_oi
  data/fresh_totals_{cu|al|zn}.csv    : date,contract,volume,long_oi,short_oi,settle
Masters (preserved across contract expiry):
  data/master_positions.csv, data/master_totals.csv
Output: data/artifact_baseline.json + shfe_live_artifact.html (from scripts/artifact_template.html)
"""
import json, os, sys
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(BASE, 'data')

mp = pd.read_csv(f'{D}/master_positions.csv', dtype={'date': str})
mt = pd.read_csv(f'{D}/master_totals.csv', dtype={'date': str})

for metal in ['cu', 'al', 'zn']:
    fp = f'{D}/fresh_positions_{metal}.csv'
    if os.path.exists(fp):
        f = pd.read_csv(fp, dtype={'date': str})
        f['metal'] = metal.upper()
        f = f[['metal', 'member', 'date', 'contract', 'long_oi', 'short_oi']]
        mp = pd.concat([mp, f], ignore_index=True)
    ft = f'{D}/fresh_totals_{metal}.csv'
    if os.path.exists(ft):
        f = pd.read_csv(ft, dtype={'date': str})
        f['metal'] = metal.upper()
        f = f[['metal', 'date', 'contract', 'volume', 'long_oi', 'short_oi', 'settle']]
        mt = pd.concat([mt, f], ignore_index=True)

mp['contract'] = mp['contract'].str.upper()
mt['contract'] = mt['contract'].str.upper()
mp = mp.drop_duplicates(subset=['metal', 'member', 'date', 'contract'], keep='last')
mt = mt.drop_duplicates(subset=['metal', 'date', 'contract'], keep='last')
mp.to_csv(f'{D}/master_positions.csv', index=False)
mt.to_csv(f'{D}/master_totals.csv', index=False)

BR = json.load(open(f'{D}/tracked_brokers.json', encoding='utf-8'))
out = {'orgCodes': BR, 'metals': {}, 'asof': ''}
for metal in ['CU', 'AL', 'ZN']:
    m = {'spread': {}, 'settle': {}, 'brokers': {}}
    tt = mt[mt.metal == metal]
    sett = {}
    for r in tt.itertuples():
        if pd.notna(r.settle):
            sett.setdefault(r.date, {})[r.contract] = r.settle
    m['settle'] = sett
    # top-20 board totals: sum over contracts per date -> [long_sum, short_sum]
    g = tt.groupby('date').agg(l=('long_oi', 'sum'), s=('short_oi', 'sum'))
    m['tot'] = {d: [round(r.l), round(r.s)] for d, r in g.iterrows() if pd.notna(r.l) and pd.notna(r.s)}
    near = {}
    for d, cs in sett.items():
        tym = d[2:4] + d[5:7]
        live = sorted([c for c in cs if c[2:] >= tym], key=lambda c: c[2:])
        near[d] = set(live[:1])  # front month only
        if len(live) >= 2:
            m['spread'][d] = round(sett[d][live[0]] - sett[d][live[1]], 1)
    # front-month top-20 totals: [long_sum, short_sum, contract] for the nearest contract per date
    ft = {}
    for r in tt.itertuples():
        if r.contract in near.get(r.date, set()) and pd.notna(r.long_oi) and pd.notna(r.short_oi):
            ft[r.date] = [round(r.long_oi), round(r.short_oi), r.contract]
    m['ftot'] = ft
    emm = mp[mp.metal == metal]
    for b in BR:
        bb = emm[emm.member == b]
        if bb.empty:
            continue
        g = bb.groupby('date').agg(l=('long_oi', 'sum'), s=('short_oi', 'sum'))
        nb = bb[bb.apply(lambda r: r['contract'] in near.get(r['date'], set()), axis=1)]
        ng = nb.groupby('date').agg(l=('long_oi', 'sum'), s=('short_oi', 'sum'))
        m['brokers'][b] = {'long': {d: round(v) for d, v in g.l.dropna().items()},
                           'short': {d: round(v) for d, v in g.s.dropna().items()},
                           'nlong': {d: round(v) for d, v in ng.l.dropna().items()},
                           'nshort': {d: round(v) for d, v in ng.s.dropna().items()}}
    bf = f'{D}/fresh_board_{metal.lower()}.json'
    if os.path.exists(bf):
        m['board'] = json.load(open(bf, encoding='utf-8'))
    out['metals'][metal] = m
    if sett:
        out['asof'] = max(out['asof'], max(sett))

rf = f'{D}/delivery_record.json'
if os.path.exists(rf):
    out['delivery_record'] = json.load(open(rf, encoding='utf-8'))

js = json.dumps(out, ensure_ascii=False, separators=(',', ':'))
open(f'{D}/artifact_baseline.json', 'w', encoding='utf-8').write(js)

tpl = open(f'{BASE}/scripts/artifact_template.html', encoding='utf-8').read()
html = tpl.replace('/*__BASELINE__*/', 'const BASELINE=' + js + ';')
open(f'{BASE}/shfe_live_artifact.html', 'w', encoding='utf-8').write(html)
print('OK asof', out['asof'], '| positions', len(mp), '| totals', len(mt), '| baseline KB', len(js) // 1024)
