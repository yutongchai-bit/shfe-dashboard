# -*- coding: utf-8 -*-
"""v3: fetch EastMoney rankings + SHFE official total OI (kx) + warrants,
rerun full analytics (coverage/surge/residual), rebuild index.html.
Run daily by GitHub Actions. Layout: repo root has data/, scripts/, vendor/.
"""
import datetime as dt
import json, os, subprocess, sys, time
import requests

BASE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(BASE, 'data')
API = 'https://datacenter-web.eastmoney.com/api/data/v1/get'
HDRS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Referer': 'https://data.eastmoney.com/'}


def get(params):
    for attempt in range(3):
        try:
            r = requests.get(API, params=params, headers=HDRS, timeout=30)
            j = r.json()
            if j.get('success'):
                return j['result']
            if '为空' in str(j.get('message', '')):
                return None
        except Exception as e:
            print('retry', attempt, e, file=sys.stderr)
            time.sleep(3)
    return None


def pages(report, columns, flt, ps=297, mx=10):
    rows = []
    for p in range(1, mx + 1):
        res = get({'reportName': report, 'columns': columns, 'pageSize': ps,
                   'pageNumber': p, 'filter': flt})
        if not res:
            break
        rows += res['data']
        if res['pages'] <= p:
            break
        time.sleep(0.5)
    return rows


def fetch_em():
    BR = json.load(open(f'{D}/tracked_brokers.json', encoding='utf-8'))
    for metal in ['CU', 'AL', 'ZN']:
        ml = metal.lower()
        trows = pages('RPT_FUTU_DAILYPOSITION',
                      'TRADE_DATE,SECURITY_CODE,MEMBER_NAME_ABBR,VOLUME,LONG_POSITION,SHORT_POSITION,SETTLE_PRICE',
                      f'(VOLUMERANK=21)(TRADE_CODE="{metal}")')
        trows = [r for r in trows if r.get('MEMBER_NAME_ABBR') == '本日合计']
        if metal == 'CU' and len(trows) < 100:
            print('GUARD: only', len(trows), 'CU totals rows — aborting to protect masters')
            sys.exit(1)
        with open(f'{D}/fresh_totals_{ml}.csv', 'w', encoding='utf-8') as f:
            f.write('date,contract,volume,long_oi,short_oi,settle\n')
            for r in trows:
                f.write(f"{r['TRADE_DATE'][:10]},{r['SECURITY_CODE']},{r.get('VOLUME','') or ''},"
                        f"{r.get('LONG_POSITION','') or ''},{r.get('SHORT_POSITION','') or ''},"
                        f"{r.get('SETTLE_PRICE','') or ''}\n")
        with open(f'{D}/fresh_positions_{ml}.csv', 'w', encoding='utf-8') as f:
            f.write('member,date,contract,long_oi,short_oi\n')
            for name, code in BR.items():
                rows = pages('RPT_FUTU_DAILYPOSITION',
                             'TRADE_DATE,SECURITY_CODE,LONG_POSITION,SHORT_POSITION',
                             f'(ORG_CODE="{code}")(TRADE_CODE="{metal}")')
                for r in rows:
                    lo = r.get('LONG_POSITION'); so = r.get('SHORT_POSITION')
                    f.write(f"{name},{r['TRADE_DATE'][:10]},{r['SECURITY_CODE']},"
                            f"{lo if lo is not None else ''},{so if so is not None else ''}\n")
                time.sleep(0.3)
        # front-month board (calendar prompt rule: day<=15 -> this month, else next)
        if trows:
            latest = max(r['TRADE_DATE'][:10] for r in trows)
            tym = latest[2:4] + latest[5:7]
            live = sorted({r['SECURITY_CODE'] for r in trows
                           if r['TRADE_DATE'][:10] == latest and r['SECURITY_CODE'][2:] >= tym},
                          key=lambda c: c[2:])
            if live:
                front = live[0]
                brows = pages('RPT_FUTU_DAILYPOSITION',
                              'ORG_NAME_ABBR_NEW,LP_RANK,LONG_POSITION,SP_RANK,SHORT_POSITION',
                              f'(SECURITY_CODE="{front}")(TRADE_DATE=\'{latest}\')', ps=97)
                skip = {'本日合计', '上日合计', '总量增减'}
                out_rows, seen = [], set()
                for r in brows:
                    n = r.get('ORG_NAME_ABBR_NEW')
                    if not n or n in skip or n in seen:
                        continue
                    seen.add(n)
                    lp = r.get('LP_RANK'); sp = r.get('SP_RANK')
                    out_rows.append([n, lp if lp not in (None, 9999) else None,
                                     r.get('LONG_POSITION'),
                                     sp if sp not in (None, 9999) else None,
                                     r.get('SHORT_POSITION')])
                json.dump({'date': latest, 'contract': front, 'rows': out_rows},
                          open(f'{D}/fresh_board_{ml}.json', 'w', encoding='utf-8'),
                          ensure_ascii=False)
        print(metal, 'EM done')


def fetch_kx():
    """SHFE official per-contract total OI (daily kx report) -> data/total_oi_cu.csv"""
    path = f'{D}/total_oi_cu.csv'
    seen = {}
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            f.readline()
            for ln in f:
                p = ln.strip().split(',')
                if len(p) == 3 and p[0]:
                    seen[(p[0], p[1])] = p[2]
    have_dates = {k[0] for k in seen}
    today = dt.date.today()
    H = {'User-Agent': HDRS['User-Agent'], 'Referer': 'https://www.shfe.com.cn/'}
    for i in range(14, -1, -1):
        d = today - dt.timedelta(days=i)
        ds = d.strftime('%Y-%m-%d')
        if d.weekday() >= 5 or ds in have_dates:
            continue
        url = f"https://www.shfe.com.cn/data/tradedata/future/dailydata/kx{d.strftime('%Y%m%d')}.dat"
        try:
            r = requests.get(url, headers=H, timeout=30)
            if r.status_code != 200:
                continue
            j = r.json()
        except Exception as e:
            print('kx skip', ds, e)
            continue
        n = 0
        for it in j.get('o_curinstrument', []):
            if str(it.get('PRODUCTID', '')).strip() != 'cu_f':
                continue
            dm = str(it.get('DELIVERYMONTH', '')).strip()
            oi = it.get('OPENINTEREST')
            if dm.isdigit() and len(dm) == 4 and oi not in (None, ''):
                seen[(ds, 'CU' + dm)] = str(int(oi))
                n += 1
        print('kx', ds, n, 'contracts')
        time.sleep(1)
    with open(path, 'w', encoding='utf-8') as f:
        f.write('date,contract,total_oi\n')
        for k in sorted(seen):
            f.write(f'{k[0]},{k[1]},{seen[k]}\n')


def fetch_warrants():
    """SHFE copper warrants (tonnes) via EastMoney -> data/warrants_cu.csv"""
    path = f'{D}/warrants_cu.csv'
    w = {}
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            f.readline()
            for ln in f:
                p = ln.strip().split(',')
                if len(p) == 2 and p[0]:
                    w[p[0]] = p[1]
    res = get({'reportName': 'RPT_FUTU_STOCKDATA',
               'columns': 'TRADE_DATE,SECURITY_CODE,ON_WARRANT_NUM',
               'pageSize': 73, 'sortColumns': 'TRADE_DATE', 'sortTypes': -1,
               'filter': '(SECURITY_CODE="CU")'})
    if res:
        for r in res['data']:
            v = r.get('ON_WARRANT_NUM')
            if v is not None:
                w[r['TRADE_DATE'][:10]] = str(int(v))
        print('warrants: latest', max(w))
    with open(path, 'w', encoding='utf-8') as f:
        f.write('date,tonnes\n')
        for d in sorted(w):
            f.write(f'{d},{w[d]}\n')


def main():
    fetch_em()
    fetch_kx()
    fetch_warrants()
    # merge fresh -> masters FIRST (so analytics sees the new day), then analytics, then rebuild
    subprocess.check_call([sys.executable, os.path.join(BASE, 'scripts', 'refresh_pipeline.py')])
    try:
        subprocess.check_call([sys.executable, os.path.join(BASE, 'scripts', 'surge_delivery_analysis.py')])
    except Exception as e:
        import traceback
        traceback.print_exc()
        print('!!! ANALYTICS FAILED — page keeps previous (stale) analytics:', e)
    # rebuild again so index picks up the fresh surge_delivery.json
    subprocess.check_call([sys.executable, os.path.join(BASE, 'scripts', 'refresh_pipeline.py')])
    src = os.path.join(BASE, 'SHFE_dashboard_standalone.html')
    if not os.path.exists(src):
        src = os.path.join(BASE, 'shfe_live_artifact.html')
    if os.path.exists(src):
        os.replace(src, os.path.join(BASE, 'index.html'))
        print('index.html rebuilt from', os.path.basename(src))


if __name__ == '__main__':
    main()
