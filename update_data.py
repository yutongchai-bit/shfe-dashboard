# -*- coding: utf-8 -*-
"""Self-contained daily refresh: fetch SHFE rankings from EastMoney, rebuild index.html.
Self-heals: recreates data files and extracts the page template from index.html if missing/corrupt."""
import io, json, os, re, sys, time
import pandas as pd
import requests

BASE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(BASE, 'data')
os.makedirs(D, exist_ok=True)
API = 'https://datacenter-web.eastmoney.com/api/data/v1/get'
HDRS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Referer': 'https://data.eastmoney.com/'}
BROKERS = {"金瑞期货":"10047016","铜冠金源":"10054001","中信期货":"10058975","国泰君安":"10083138",
 "永安期货":"10102950","银河期货":"10106342","东证期货":"10123207","建信期货":"10096959",
 "五矿期货":"10053996","中金岭南":"10067237","国贸期货":"10019440","紫金天风":"10400243",
 "中粮期货":"10098586","光大期货":"10106292"}

def get(params):
    for a in range(3):
        try:
            r = requests.get(API, params=params, headers=HDRS, timeout=30)
            j = r.json()
            if j.get('success'): return j['result']
            if '为空' in str(j.get('message','')): return None
        except Exception as e:
            print('retry', a, e, file=sys.stderr); time.sleep(3)
    return None

def pages(report, columns, flt, ps=300, mx=10):
    rows = []
    for p in range(1, mx+1):
        res = get({'reportName':report,'columns':columns,'pageSize':ps,'pageNumber':p,'filter':flt})
        if not res: break
        rows += res['data']
        if res['pages'] <= p: break
        time.sleep(0.4)
    return rows

def load_master(path, cols):
    try:
        df = pd.read_csv(path, dtype={'date':str})
        if list(df.columns) == cols: return df
    except Exception: pass
    return pd.DataFrame(columns=cols)

def extract_baseline_and_template():
    html = open(os.path.join(BASE,'index.html'), encoding='utf-8').read()
    i = html.index('const BASELINE=')
    j = html.index(';\nconst DELIV_DEFAULT', i)
    baseline = json.loads(html[i+len('const BASELINE='):j])
    tpl = html[:i] + '/*__BASELINE__*/' + html[j+1:]
    return baseline, tpl

def main():
    old_baseline, tpl = extract_baseline_and_template()
    json.dump(BROKERS, open(f'{D}/tracked_brokers.json','w',encoding='utf-8'), ensure_ascii=False)
    if 'delivery_record' in old_baseline:
        json.dump(old_baseline['delivery_record'], open(f'{D}/delivery_record.json','w',encoding='utf-8'), ensure_ascii=False)

    MPC = ['metal','member','date','contract','long_oi','short_oi']
    MTC = ['metal','date','contract','volume','long_oi','short_oi','settle']
    mp = load_master(f'{D}/master_positions.csv', MPC)
    mt = load_master(f'{D}/master_totals.csv', MTC)

    boards = {}
    new_mp, new_mt = [], []
    for metal in ['CU','AL','ZN']:
        trows = pages('RPT_FUTU_DAILYPOSITION',
            'TRADE_DATE,SECURITY_CODE,MEMBER_NAME_ABBR,VOLUME,LONG_POSITION,SHORT_POSITION,SETTLE_PRICE',
            f'(VOLUMERANK=21)(TRADE_CODE="{metal}")')
        trows = [r for r in trows if r.get('MEMBER_NAME_ABBR')=='本日合计']
        for r in trows:
            new_mt.append([metal, r['TRADE_DATE'][:10], r['SECURITY_CODE'],
                           r.get('VOLUME'), r.get('LONG_POSITION'), r.get('SHORT_POSITION'), r.get('SETTLE_PRICE')])
        for name, code in BROKERS.items():
            rows = pages('RPT_FUTU_DAILYPOSITION','TRADE_DATE,SECURITY_CODE,LONG_POSITION,SHORT_POSITION',
                         f'(ORG_CODE="{code}")(TRADE_CODE="{metal}")')
            for r in rows:
                new_mp.append([metal, name, r['TRADE_DATE'][:10], r['SECURITY_CODE'],
                               r.get('LONG_POSITION'), r.get('SHORT_POSITION')])
            time.sleep(0.2)
        if trows:
            latest = max(r['TRADE_DATE'][:10] for r in trows)
            tym = latest[2:4]+latest[5:7]
            live = sorted({r['SECURITY_CODE'] for r in trows
                           if r['TRADE_DATE'][:10]==latest and r['SECURITY_CODE'][2:]>=tym}, key=lambda c:c[2:])
            if live:
                brows = pages('RPT_FUTU_DAILYPOSITION',
                    'ORG_NAME_ABBR_NEW,LP_RANK,LONG_POSITION,SP_RANK,SHORT_POSITION',
                    f'(SECURITY_CODE="{live[0]}")(TRADE_DATE=\'{latest}\')', ps=100)
                skip = {'本日合计','上日合计','总量增减'}; seen=set(); out=[]
                for r in brows:
                    n = r.get('ORG_NAME_ABBR_NEW')
                    if not n or n in skip or n in seen: continue
                    seen.add(n)
                    lp, sp = r.get('LP_RANK'), r.get('SP_RANK')
                    out.append([n, lp if lp not in (None,9999) else None, r.get('LONG_POSITION'),
                                sp if sp not in (None,9999) else None, r.get('SHORT_POSITION')])
                boards[metal] = {'date':latest,'contract':live[0],'rows':out}
        print(metal, 'fetched')

    if len(new_mt) < 100:
        print('Data source returned too little — keeping existing page.', file=sys.stderr)
        sys.exit(1)

    mp = pd.concat([mp, pd.DataFrame(new_mp, columns=MPC)], ignore_index=True)
    mt = pd.concat([mt, pd.DataFrame(new_mt, columns=MTC)], ignore_index=True)
    for df in (mp, mt): df['contract'] = df['contract'].str.upper()
    mp = mp.drop_duplicates(subset=['metal','member','date','contract'], keep='last')
    mt = mt.drop_duplicates(subset=['metal','date','contract'], keep='last')
    mp.to_csv(f'{D}/master_positions.csv', index=False)
    mt.to_csv(f'{D}/master_totals.csv', index=False)

    out = {'orgCodes':BROKERS,'metals':{},'asof':''}
    for metal in ['CU','AL','ZN']:
        m = {'spread':{},'settle':{},'brokers':{}}
        tt = mt[mt.metal==metal]
        sett = {}
        for r in tt.itertuples():
            if pd.notna(r.settle): sett.setdefault(r.date,{})[r.contract] = r.settle
        m['settle'] = sett
        g = tt.groupby('date').agg(l=('long_oi','sum'), s=('short_oi','sum'))
        m['tot'] = {d:[round(r.l),round(r.s)] for d,r in g.iterrows() if pd.notna(r.l) and pd.notna(r.s)}
        near = {}
        for d, cs in sett.items():
            tym = d[2:4]+d[5:7]
            live = sorted([c for c in cs if c[2:]>=tym], key=lambda c:c[2:])
            near[d] = set(live[:1])
            if len(live)>=2: m['spread'][d] = round(sett[d][live[0]]-sett[d][live[1]],1)
        ft = {}
        for r in tt.itertuples():
            if r.contract in near.get(r.date,set()) and pd.notna(r.long_oi) and pd.notna(r.short_oi):
                ft[r.date] = [round(r.long_oi), round(r.short_oi), r.contract]
        m['ftot'] = ft
        emm = mp[mp.metal==metal]
        for b in BROKERS:
            bb = emm[emm.member==b]
            if bb.empty: continue
            g = bb.groupby('date').agg(l=('long_oi','sum'), s=('short_oi','sum'))
            nb = bb[bb.apply(lambda r: r['contract'] in near.get(r['date'],set()), axis=1)]
            ng = nb.groupby('date').agg(l=('long_oi','sum'), s=('short_oi','sum'))
            m['brokers'][b] = {'long':{d:round(v) for d,v in g.l.dropna().items()},
                               'short':{d:round(v) for d,v in g.s.dropna().items()},
                               'nlong':{d:round(v) for d,v in ng.l.dropna().items()},
                               'nshort':{d:round(v) for d,v in ng.s.dropna().items()}}
        if metal in boards: m['board'] = boards[metal]
        elif old_baseline['metals'].get(metal,{}).get('board'): m['board'] = old_baseline['metals'][metal]['board']
        out['metals'][metal] = m
        if sett: out['asof'] = max(out['asof'], max(sett))
    if 'delivery_record' in old_baseline: out['delivery_record'] = old_baseline['delivery_record']

    js = json.dumps(out, ensure_ascii=False, separators=(',',':'))
    open(os.path.join(BASE,'index.html'),'w',encoding='utf-8').write(
        tpl.replace('/*__BASELINE__*/','const BASELINE='+js+';'))
    print('OK asof', out['asof'], '| totals', len(mt), '| positions', len(mp))

if __name__ == '__main__':
    main()
if __name__ == '__main__':
    main()
