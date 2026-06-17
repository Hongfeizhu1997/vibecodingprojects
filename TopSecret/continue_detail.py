#!/usr/bin/env python3
"""Continue scraping xsharing detail pages - 500s run"""
import json, re, time, requests, sys
from datetime import datetime

INP = '/root/ClaudeProjects/TopSecret/output/xsharing_posts_v2.json'
OUT = '/root/ClaudeProjects/TopSecret/output/xsharing_results_v2.json'

with open(INP) as f:
    posts = json.load(f)

with open(OUT) as f:
    results = json.load(f)

# Find missing
missing = [p for p in posts if str(p['post_id']) not in results]
print(f"Total posts: {len(posts)}, already scraped: {len(results)}, remaining: {len(missing)}")
print(f"Starting scrape at {datetime.now().strftime('%H:%M:%S')}...")
sys.stdout.flush()

s = requests.Session()
s.headers.update({'User-Agent': 'Mozilla/5.0'})

start_time = time.time()
deadline = start_time + 490  # leave 10s margin
scraped_this_run = 0
errors = 0
save_every = 20

for i, p in enumerate(missing):
    if time.time() > deadline:
        remaining = len(missing) - i
        print(f"\nTime limit reached ({time.time()-start_time:.0f}s). {remaining} posts remaining.")
        break
    
    try:
        html = s.get(p['url'], timeout=3).text
        dl = re.search(r'已有.*?(\d+).*?人解锁下载', html)
        dl_num = int(dl.group(1)) if dl else 0
        results[p['post_id']] = {**p, 'downloads': dl_num}
        scraped_this_run += 1
    except requests.Timeout:
        results[p['post_id']] = {**p, 'downloads': -1}  # -1 = timeout
        errors += 1
    except Exception as e:
        results[p['post_id']] = {**p, 'downloads': -2}  # -2 = error
        errors += 1
    
    # Save every 20
    if (scraped_this_run + errors) % save_every == 0:
        with open(OUT, 'w') as f:
            json.dump(results, f, ensure_ascii=False)
        elapsed = time.time() - start_time
        remaining = len(missing) - i - 1
        rate = (scraped_this_run + errors) / elapsed if elapsed > 0 else 0
        print(f"  [{elapsed:.0f}s] Processed {scraped_this_run + errors}, saved. Results: {len(results)}, remaining: {remaining}, rate: {rate:.1f}/s")
        sys.stdout.flush()

# Final save
with open(OUT, 'w') as f:
    json.dump(results, f, ensure_ascii=False)

total_time = time.time() - start_time
still_remaining = len([p for p in posts if str(p['post_id']) not in results])

print(f"\n{'='*50}")
print(f"Run complete at {datetime.now().strftime('%H:%M:%S')}")
print(f"Duration: {total_time:.0f}s")
print(f"Scraped this run: {scraped_this_run}")
print(f"Errors/timeouts: {errors}")
print(f"Total details now: {len(results)}")
print(f"Still remaining: {still_remaining}")
print(f"Rate: {(scraped_this_run+errors)/total_time:.1f} req/s" if total_time > 0 else "")
print(f"{'='*50}")
