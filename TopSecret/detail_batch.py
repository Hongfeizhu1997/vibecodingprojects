#!/usr/bin/env python3
import json, re, time, requests, sys

s = requests.Session()
s.headers.update({'User-Agent': 'Mozilla/5.0'})

with open('/root/ClaudeProjects/TopSecret/output/xsharing_posts_v2.json') as f:
    posts = json.load(f)

with open('/root/ClaudeProjects/TopSecret/output/xsharing_results_v2.json') as f:
    results = json.load(f)

todo = [p for p in posts if p['post_id'] not in results]
batch = int(sys.argv[1]) if len(sys.argv) > 1 else 100
todo = todo[:batch]

print(f'处理 {len(todo)} 篇 (剩余 {len(posts)-len(results)-len(todo)} 待处理)...')

for i, p in enumerate(todo):
    try:
        html = s.get(p['url'], timeout=8).text
        dl = re.search(r'\u5df2\u6709.*?(\d+).*?\u4eba\u89e3\u9501\u4e0b\u8f7d', html)
        dl_num = int(dl.group(1)) if dl else 0
        results[p['post_id']] = {**p, 'downloads': dl_num}
        if (i+1) % 20 == 0:
            print(f'  {i+1}/{len(todo)} ...')
    except Exception as e:
        results[p['post_id']] = {**p, 'downloads': 0}

with open('/root/ClaudeProjects/TopSecret/output/xsharing_results_v2.json', 'w') as f:
    json.dump(results, f, ensure_ascii=False)
print(f'Done: {len(results)} 篇')
