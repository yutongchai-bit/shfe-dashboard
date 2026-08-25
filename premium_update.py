# -*- coding: utf-8 -*-
"""Best-effort daily SMM copper spot premium from free news articles. Never fails the build."""
import os, re, datetime
import requests

BASE = os.path.dirname(os.path.abspath(__file__))
PF = os.path.join(BASE, 'data', 'premium.csv')
H = {'User-Agent': 'Mozilla/5.0'}

def fetch(url):
    try:
        return requests.get(url, headers=H, timeout=30).text
    except Exception:
        return ''

def main():
    try:
        seen = {l.split(',')[0].strip() for l in open(PF, encoding='utf-8') if ',' in l}
    except FileNotFoundError:
        seen = set()
    listing = fetch('https://news.metal.com/en/copper') + fetch('https://news.metal.com/en/')
    links = re.findall(r'href="(https://news\.metal\.com/en/newscontent/\d+[^"]*)"', listing)
    links += ['https://news.metal.com' + l for l in re.findall(r'href="(/en/newscontent/\d+[^"]*)"', listing)]
    cand = [l for l in dict.fromkeys(links) if re.search(r'spot-copper|copper-morning|premium', l)][:8]
    months = {m: i+1 for i, m in enumerate(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'])}
    added = 0
    for url in cand:
        txt = fetch(url)
        dm = re.search(r'Published:\s*([A-Z][a-z]{2})\s+(\d{1,2}),\s*(\d{4})', txt)
        if not dm:
            continue
        d = datetime.date(int(dm.group(3)), months.get(dm.group(1), 1), int(dm.group(2)))
        target = d if 'spot-copper' in url else d - datetime.timedelta(days=1)
        while target.weekday() >= 5:
            target -= datetime.timedelta(days=1)
        m = re.search(r'standard-quality copper[^.]{0,120}?(premium|discount)s? of (\d+)(?:\s*[-~]\s*(\d+))?\s*yuan/mt', txt, re.I)
        if not m:
            m = re.search(r'(premium|discount)s? of (\d+)(?:\s*[-~]\s*(\d+))?\s*yuan/mt[^.]{0,80}?(?:front|current)-month', txt, re.I)
        if not m:
            continue
        v = (int(m.group(2)) + int(m.group(3) or m.group(2))) / 2.0
        if m.group(1).lower() == 'discount':
            v = -v
        ds = target.strftime('%Y-%m-%d')
        if ds in seen:
            continue
        with open(PF, 'a', encoding='utf-8') as f:
            f.write(f'{ds},{v:g}\n')
        seen.add(ds)
        added += 1
        print('premium added', ds, v)
    print('premium rows added:', added)

if __name__ == '__main__':
    main()
