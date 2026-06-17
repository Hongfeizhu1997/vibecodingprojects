#!/usr/bin/env python3
"""Async parallel xsharing detail scraper using aiohttp."""
import json
import re
import time
import asyncio
import sys
import os
import aiohttp
import ssl

INP = '/root/ClaudeProjects/TopSecret/output/xsharing_posts_v2.json'
OUT = '/root/ClaudeProjects/TopSecret/output/xsharing_results_v2.json'
CONCURRENCY = 12
TIMEOUT = 3
SAVE_EVERY = 50
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'

# Load posts and existing results
with open(INP) as f:
    posts = json.load(f)

results = {}
with open(OUT) as f:
    results = json.load(f)

# Find unscraped
todo = [p for p in posts if p['post_id'] not in results]

def flush(s):
    print(s)
    sys.stdout.flush()

flush(f"Total posts: {len(posts)}")
flush(f"Already scraped: {len(results)}")
flush(f"Remaining to scrape: {len(todo)}")
flush(f"Concurrency: {CONCURRENCY}, timeout: {TIMEOUT}s")

scraped = 0
errors = 0
timeouts = 0
save_lock = asyncio.Lock()
start_time = time.time()

async def fetch_detail(session, sem, idx, post):
    global scraped, errors, timeouts
    async with sem:
        pid = post['post_id']
        try:
            timeout = aiohttp.ClientTimeout(total=TIMEOUT)
            async with session.get(post['url'], timeout=timeout) as resp:
                if resp.status != 200:
                    results[pid] = {**post, 'downloads': -1}
                    errors += 1
                    return
                html = await resp.text()
                dl = re.search(r'已有.*?(\d+).*?人解锁下载', html)
                dl_num = int(dl.group(1)) if dl else 0
                results[pid] = {**post, 'downloads': dl_num}
                scraped += 1
        except (asyncio.TimeoutError, aiohttp.ClientTimeoutError):
            results[pid] = {**post, 'downloads': -1}  # -1 = timeout
            timeouts += 1
        except Exception:
            results[pid] = {**post, 'downloads': -2}  # -2 = other error
            errors += 1

    # Save every SAVE_EVERY
    total_done = scraped + errors + timeouts
    if total_done % SAVE_EVERY == 0:
        async with save_lock:
            with open(OUT, 'w') as f:
                json.dump(results, f, ensure_ascii=False)
            elapsed = time.time() - start_time
            remaining = len(todo) - total_done
            rate = total_done / elapsed if elapsed > 0 else 0
            pct = total_done / len(todo) * 100 if len(todo) > 0 else 100
            flush(f"  [{elapsed:.0f}s] {total_done}/{len(todo)} ({pct:.1f}%) | "
                  f"OK:{scraped} err:{errors} to:{timeouts} rate:{rate:.1f}/s rem:{remaining}")


async def main():
    # Create SSL context that doesn't verify certs (site has Cloudflare cert issues)
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    connector = aiohttp.TCPConnector(limit=CONCURRENCY, limit_per_host=CONCURRENCY, ssl=ssl_context)
    sem = asyncio.Semaphore(CONCURRENCY)
    async with aiohttp.ClientSession(
        connector=connector,
        headers={'User-Agent': UA}
    ) as session:
        tasks = [fetch_detail(session, sem, i, p) for i, p in enumerate(todo)]
        await asyncio.gather(*tasks)

    # Final save
    with open(OUT, 'w') as f:
        json.dump(results, f, ensure_ascii=False)

    # Report
    total_time = time.time() - start_time
    still_remaining = len([p for p in posts if p['post_id'] not in results])
    
    flush(f"\n{'='*50}")
    flush(f"Async run complete!")
    flush(f"Duration: {total_time:.0f}s")
    flush(f"Scraped this run: {scraped}")
    flush(f"Errors: {errors}")
    flush(f"Timeouts: {timeouts}")
    flush(f"Total details now: {len(results)}")
    flush(f"Still remaining: {still_remaining}")
    if total_time > 0:
        flush(f"Rate: {(scraped+errors+timeouts)/total_time:.1f} req/s")
    flush(f"{'='*50}")


if __name__ == '__main__':
    asyncio.run(main())
