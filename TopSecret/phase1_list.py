#!/usr/bin/env python3
"""Xsharing 全量爬虫 - Phase 1: 列表"""
import re, json, time, requests
from datetime import datetime, timedelta

BASE = 'https://game.xsharing.cc'
OUT = '/root/ClaudeProjects/TopSecret/output/xsharing_posts_v2.json'
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
stop = datetime.now() - timedelta(days=180)
s = requests.Session(); s.headers.update(H)
posts = {}

for page in range(1, 501):
    url = f'{BASE}/page/{page}' if page > 1 else BASE
    try: html = s.get(url, timeout=15).text
    except: print(f'  p{page}: ERR'); continue
    entries = re.finditer(r'<article[^>]*>.*?href="(https://game\.xsharing\.cc/(\d+)\.html)".*?</article>', html, re.DOTALL)
    cnt = 0
    for e in entries:
        block, pid, link = e.group(0), e.group(2), e.group(1)
        if pid in posts: continue
        dm = re.search(r'(\d+\s*(?:秒|分|分钟|小时|天|周|个?月|年)前)', block)
        if not dm: continue
        txt = dm.group(1); d = None; now = datetime.now()
        for pat, unit in [(r'(\d+)\s*秒前','s'),(r'(\d+)\s*分前','m'),(r'(\d+)\s*分钟前','m'),
                          (r'(\d+)\s*小时前','h'),(r'(\d+)\s*天前','d'),(r'(\d+)\s*周前','w'),
                          (r'(\d+)\s*个月前','M'),(r'(\d+)\s*月前','M'),(r'(\d+)\s*年前','y')]:
            m = re.match(pat, txt)
            if m:
                n = int(m.group(1))
                if unit=='s': d=now-timedelta(seconds=n)
                elif unit=='m': d=now-timedelta(minutes=n)
                elif unit=='h': d=now-timedelta(hours=n)
                elif unit=='d': d=now-timedelta(days=n)
                elif unit=='w': d=now-timedelta(weeks=n)
                elif unit=='M': d=now-timedelta(days=n*30)
                elif unit=='y': d=now-timedelta(days=n*365)
                break
        if not d or d < stop: continue
        tm = re.search(r'<h[23][^>]*>(.*?)</h[23]>', block, re.DOTALL)
        title = re.sub(r'<[^>]+>', '', tm.group(1)).strip()[:120] if tm else ''
        cm = re.search(r'<a[^>]*category[^>]*>(.*?)</a>', block)
        cat = cm.group(1).strip() if cm else ''
        posts[pid] = {'post_id':pid,'url':link,'title':title,'category':cat,'date':d.strftime('%Y-%m-%d')}
        cnt += 1
    print(f'  p{page:3}: +{cnt} ({len(posts)})')
    if page % 20 == 0:
        with open(OUT,'w') as f: json.dump(list(posts.values()), f, ensure_ascii=False)
    time.sleep(0.12)

with open(OUT,'w') as f: json.dump(list(posts.values()), f, ensure_ascii=False)
print(f'Done: {len(posts)} posts -> {OUT}')
