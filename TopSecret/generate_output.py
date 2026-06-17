#!/usr/bin/env python3
import json
from datetime import datetime
from pathlib import Path

BASE = Path('/root/ClaudeProjects/TopSecret')
OUTPUT = BASE / 'output'
WIKI = Path('/root/wiki/TopSecret')
WIKI.mkdir(parents=True, exist_ok=True)
today = datetime.now().strftime('%Y-%m-%d')

with open(OUTPUT / 'xsharing_results_v2.json') as f:
    results = json.load(f)

posts = sorted(results.values(), key=lambda x: x.get('downloads', 0), reverse=True)
print(f'总数: {len(posts)} 篇')

# JSON
json_path = OUTPUT / f'xsharing-{today}.json'
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump({'source': 'xsharing.org', 'date': today, 'total': len(posts), 'posts': posts},
              f, ensure_ascii=False, indent=2)
print(f'JSON: {json_path}')

# MD
md_path = OUTPUT / f'xsharing-{today}.md'
lines = [
    f'# Xsharing \u2014 \u8fd1\u534a\u5e74\u5e16\u5b50 (\u6309\u89e3\u9501\u4e0b\u8f7d\u6392\u5e8f)',
    '',
    f'> \u66f4\u65b0\u65f6\u95f4: {today} | \u603b\u6570: {len(posts)} \u7bc7 | \u7a97\u53e3: 180\u5929',
    '',
    '| # | \u89e3\u9501 | \u6807\u9898 | \u5206\u7c7b | \u65e5\u671f |',
    '|---|------|------|------|------|',
]
for i, d in enumerate(posts[:100], 1):
    title = d['title'][:40]
    lines.append(f'| {i} | {d["downloads"]} | [{title}]({d["url"]}) | {d["category"]} | {d["date"]} |')

lines.append('')
lines.append('---')
lines.append('')
for i, d in enumerate(posts[:30], 1):
    lines.append(f'## {i}. {d["title"]} ({d["downloads"]}\u4eba\u89e3\u9501)')
    lines.append(f'- \u5206\u7c7b: {d["category"]} | \u65e5\u671f: {d["date"]}')
    lines.append(f'- \u94fe\u63a5: {d["url"]}')
    lines.append('')

with open(md_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print(f'MD: {md_path}')

# Wiki
wiki_path = WIKI / f'xsharing-\u6392\u884c-{today}.md'
with open(wiki_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print(f'Wiki: {wiki_path}')

# Top 10
print('\nTop 10:')
for i, d in enumerate(posts[:10], 1):
    print(f'  {i:2}. [{d["downloads"]:4}\u4eba] {d["title"][:50]} ({d["date"]})')

# 统计
dates = set(d['date'] for d in posts)
print(f'\n日期跨度: {min(dates)} ~ {max(dates)} ({len(dates)} \u5929)')
dl_gt0 = sum(1 for p in posts if p['downloads'] > 0)
print(f'\u6709\u4e0b\u8f7d\u91cf: {dl_gt0}/{len(posts)}')
