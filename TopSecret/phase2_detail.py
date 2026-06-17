#!/usr/bin/env python3
"""Xsharing 全量爬虫 - Phase 2: 详情"""
import re, json, time, requests, os

INP = '/root/ClaudeProjects/TopSecret/output/xsharing_posts_v2.json'
OUT = '/root/ClaudeProjects/TopSecret/output/xsharing_results_v2.json'

with open(INP) as f: posts = json.load(f)
results = {}
if os.path.exists(OUT):
    with open(OUT) as f: results = json.load(f)

s = requests.Session()
s.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})

todo = [p for p in posts if p['post_id'] not in results]
print(f'待处理: {len(todo)} / 总: {len(posts)}')

for i, p in enumerate(todo):
    try:
        html = s.get(p['url'], timeout=10).text
        dl = re.search(r'已有.*?(\d+).*?人解锁下载', html)
        results[p['post_id']] = {**p, 'downloads': int(dl.group(1)) if dl else 0}
    except:
        results[p['post_id']] = {**p, 'downloads': 0}
    time.sleep(0.08)
    if (i+1) % 100 == 0:
        with open(OUT, 'w') as f: json.dump(results, f, ensure_ascii=False)
        print(f'  {i+1}/{len(todo)} [{len(results)}篇]')

with open(OUT, 'w') as f: json.dump(results, f, ensure_ascii=False)
ranked = sorted(results.values(), key=lambda x: x['downloads'], reverse=True)
print(f'\nDone: {len(results)} 篇')
for i, d in enumerate(ranked[:20], 1):
    print(f'{i:2}. [{d["downloads"]:4}人] {d["title"][:55]}')
