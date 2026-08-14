# -*- coding: utf-8 -*-
"""Fetch latest SHFE top-20 ranking data from EastMoney and rebuild index.html."""
import json, os, sys, time
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

def pages(report, columns, flt, page_size=300, max_pages=10):
    rows = []
    for p in range(1, max_pages + 1):
        res = get({'reportName': report, 'columns': columns, 'pageSize': page_size,
                   'pageNumber': p, 'filter': flt})
        if not res:
            break
        rows += res['data']
        if res['pages'] <= p:
            break
        time.sleep(0.5)
    return rows

def main():
    BR = json.load(open(f'{D}/tracked_brokers.json', encoding='utf-8'))
    for metal in ['CU', 'AL', 'ZN']:
        ml = metal.lower()
        trows = pages('RPT_FUTU_DAILYPOSITION',
                      'TRADE_DATE,SECURITY_CODE,MEMBER_NAME_ABBR,VOLUME,LONG_POSITION,SHORT_POSITION,SETTLE_PRICE',
                      f'(VOLUMERANK=21)(TRADE_CODE="{metal}")')
        trows = [r for r in trows if r.get('MEMBER_NAME_ABBR') == '本日合计']
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
                              f'(SECURITY_CODE="{front}")(TRADE_DATE=\'{latest}\')', page_size=100)
                skip = {'本日合计', '上日合计', '总量增减'}
                out_rows = []
                seen = set()
                for r in brows:
                    n = r.get('ORG_NAME_ABBR_NEW')
                    if not n or n in skip or n in seen:
                        continue
                    seen.add(n)
                    lp = r.get('LP_RANK'); sp = r.get('SP_RANK')
                    out_rows.append([n,
                                     lp if lp not in (None, 9999) else None,
                                     r.get('LONG_POSITION'),
                                     sp if sp not in (None, 9999) else None,
                                     r.get('SHORT_POSITION')])
                json.dump({'date': latest, 'contract': front, 'rows': out_rows},
                          open(f'{D}/fresh_board_{ml}.json', 'w', encoding='utf-8'),
                          ensure_ascii=False)
        print(metal, 'done')
    import subprocess
    subprocess.check_call([sys.executable, os.path.join(BASE, 'scripts', 'refresh_pipeline.py')])
    src = os.path.join(BASE, 'shfe_live_artifact.html')
    if os.path.exists(src):
        os.replace(src, os.path.join(BASE, 'index.html'))
    print('index.html rebuilt')

if __name__ == '__main__':
    main()
