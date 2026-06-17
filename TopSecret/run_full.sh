#!/bin/bash
# Xsharing 200页全量爬取
set -e
pip install -q requests 2>/dev/null

python3 << 'PYEOF'
import re, json, time, requests, os
from datetime import datetime, timedelta

BASE = 'https://game.xsharing.cc'
OUT = '/root/ClaudeProjects/TopSecret/output/xsharing_posts_v2.json'
RES = '/root/ClaudeProjects/TopSecret/output/xsharing_results_v2.json'
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
stop = datetime.now() - timedelta(days=90)
s = requests.Session(); s.headers.update(H)

# ====== Phase 1: 列表 ======
print("Phase 1: 爬取200页列表...")
posts = {}

for page in range(1, 201):
    url = f'{BASE}/page/{page}' if page > 1 else BASE
    try:
        html = s.get(url, timeout=15).text
    except Exception as e:
        print(f'  p{page}: ERR'); continue
    
    entries = re.finditer(r'<article[^>]*>.*?href="(https://game\.xsharing\.cc/(\d+)\.html)".*?</article>', html, re.DOTALL)
    cnt = 0
    for e in entries:
        block, pid, link = e.group(0), e.group(2), e.group(1)
        if pid in posts: continue
        
        # 只使用相对日期
        dm = re.search(r'(\d+\s*(?:秒|分|分钟|小时|天|周|个?月|年)前)', block)
        if not dm: continue
        d = None
        txt = dm.group(1)
        now = datetime.now()
        m = re.match(r'(\d+)\s*秒前', txt)
        if m: d = now - timedelta(seconds=int(m.group(1)))
        m = re.match(r'(\d+)\s*分前', txt)
        if m: d = now - timedelta(minutes=int(m.group(1)))
        m = re.match(r'(\d+)\s*小时前', txt)
        if m: d = now - timedelta(hours=int(m.group(1)))
        m = re.match(r'(\d+)\s*天前', txt)
        if m: d = now - timedelta(days=int(m.group(1)))
        m = re.match(r'(\d+)\s*周前', txt)
        if m: d = now - timedelta(weeks=int(m.group(1)))
        m = re.match(r'(\d+)\s*个月前', txt)
        if m: d = now - timedelta(days=int(m.group(1))*30)
        m = re.match(r'(\d+)\s*年前', txt)
        if m: d = now - timedelta(days=int(m.group(1))*365)
        if not d or d < stop: continue
        
        tm = re.search(r'<h[23][^>]*>(.*?)</h[23]>', block, re.DOTALL)
        title = re.sub(r'<[^>]+>', '', tm.group(1)).strip()[:120] if tm else ''
        cm = re.search(r'<a[^>]*category[^>]*>(.*?)</a>', block)
        cat = cm.group(1).strip() if cm else ''
        posts[pid] = {'post_id': pid, 'url': link, 'title': title, 'category': cat, 'date': d.strftime('%Y-%m-%d')}
        cnt += 1
    
    print(f'  p{page:3}: +{cnt} (累计{len(posts)})')
    time.sleep(0.15)
    
    # 每20页自动保存
    if page % 20 == 0:
        with open(OUT, 'w') as f:
            json.dump(list(posts.values()), f, ensure_ascii=False)

posts_list = list(posts.values())
with open(OUT, 'w') as f:
    json.dump(posts_list, f, ensure_ascii=False)
print(f'\nPhase 1 完成: {len(posts_list)} 篇')

# ====== Phase 2: 详情 ======
print(f'\nPhase 2: 爬取详情页...')
results = {}
if os.path.exists(RES):
    with open(RES) as f: results = json.load(f)

todo = [p for p in posts_list if p['post_id'] not in results]
print(f'  待处理: {len(todo)}')

for i, p in enumerate(todo):
    try:
        html = s.get(p['url'], timeout=10).text
        dl_m = re.search(r'已有.*?(\d+).*?人解锁下载', html)
        results[p['post_id']] = {**p, 'downloads': int(dl_m.group(1)) if dl_m else 0}
    except:
        results[p['post_id']] = {**p, 'downloads': 0}
    time.sleep(0.1)
    if (i+1) % 100 == 0:
        with open(RES, 'w') as f:
            json.dump(results, f, ensure_ascii=False)
        print(f'  {i+1}/{len(todo)}')

with open(RES, 'w') as f:
    json.dump(results, f, ensure_ascii=False)

ranked = sorted(results.values(), key=lambda x: x['downloads'], reverse=True)
print(f'\nPhase 2 完成! {len(results)} 篇')
print(f'\nTop 20:')
for i, d in enumerate(ranked[:20], 1):
    print(f'{i:2}. [{d["downloads"]:4}人] {d["title"][:55]} ({d["date"]})')
PYEOF
echo "ALL_DONE"
