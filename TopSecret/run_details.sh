#!/bin/bash
pip install -q requests 2>/dev/null
python3 -c "
import re, json, time, requests

with open('/root/ClaudeProjects/TopSecret/output/xsharing_posts.json') as f: posts = json.load(f)
with open('/root/ClaudeProjects/TopSecret/output/xsharing_results.json') as f: results = json.load(f)

s = requests.Session()
s.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})

todo = [p for p in posts if p['post_id'] not in results]
print(f'待处理: {len(todo)}')

for i, p in enumerate(todo):
    try:
        html = s.get(p['url'], timeout=10).text
        dl = re.search(r'已有.*?(\d+).*?人解锁下载', html)
        results[p['post_id']] = {**p, 'downloads': int(dl.group(1)) if dl else 0}
    except:
        results[p['post_id']] = {**p, 'downloads': 0}
    time.sleep(0.1)
    if (i+1) % 100 == 0:
        with open('/root/ClaudeProjects/TopSecret/output/xsharing_results.json', 'w') as f:
            json.dump(results, f, ensure_ascii=False)
        print(f'  {i+1}/{len(todo)} 已保存')

with open('/root/ClaudeProjects/TopSecret/output/xsharing_results.json', 'w') as f:
    json.dump(results, f, ensure_ascii=False)

ranked = sorted(results.values(), key=lambda x: x['downloads'], reverse=True)
print(f'Done: {len(results)} articles')
for i, d in enumerate(ranked[:20], 1):
    print(f'{i:2}. [{d[\"downloads\"]:4}] {d[\"title\"][:55]}')
"
echo "SCRIPT_DONE"
