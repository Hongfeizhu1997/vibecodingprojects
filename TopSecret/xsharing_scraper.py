#!/usr/bin/env python3
"""
Xsharing 爬虫 — 支持全量和增量模式
  全量: python3 xsharing_scraper.py
  增量: python3 xsharing_scraper.py --incremental   (每周 cron 用)
"""

import re
import json
import time
import argparse
from pathlib import Path
from datetime import datetime, timedelta

import requests

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# Obsidian Wiki 输出目录
WIKI_DIR = Path("/root/wiki/TopSecret")
WIKI_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = "https://game.xsharing.cc"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
}
SESSION = requests.Session()
SESSION.headers.update(HEADERS)

MAX_AGE_DAYS = 180
INCREMENTAL_WINDOW_DAYS = 7   # 增量模式: 已知帖子超过此天数即停止翻页
REFRESH_TOP_N = 100            # 增量模式: 刷新 Top N 已有帖子的下载量


# ── 日期解析 ──────────────────────────────────────────

def parse_relative_date(text):
    text = text.strip()
    now = datetime.now()
    m = re.match(r'(\d+)\s*秒前', text)
    if m: return now - timedelta(seconds=int(m.group(1)))
    m = re.match(r'(\d+)\s*分前', text)
    if m: return now - timedelta(minutes=int(m.group(1)))
    m = re.match(r'(\d+)\s*小时前', text)
    if m: return now - timedelta(hours=int(m.group(1)))
    m = re.match(r'(\d+)\s*天前', text)
    if m: return now - timedelta(days=int(m.group(1)))
    m = re.match(r'(\d+)\s*周前', text)
    if m: return now - timedelta(weeks=int(m.group(1)))
    m = re.match(r'(\d+)\s*个月前', text)
    if m: return now - timedelta(days=int(m.group(1)) * 30)
    m = re.match(r'(\d+)\s*月前', text)
    if m: return now - timedelta(days=int(m.group(1)) * 30)
    m = re.match(r'(\d+)\s*年前', text)
    if m: return now - timedelta(days=int(m.group(1)) * 365)
    return None


def extract_date(html_snippet):
    m = re.search(r'(\d+\s*(?:秒|分|分钟|小时|天|周|个?月|年)前)', html_snippet)
    if m:
        return parse_relative_date(m.group(1))
    return None


# ── 加载历史数据 ──────────────────────────────────────

def load_previous_results():
    """加载最近一次抓取结果, 返回 {post_id: detail_dict}"""
    json_files = sorted(OUTPUT_DIR.glob("xsharing-*.json"), reverse=True)
    if not json_files:
        print("  (无历史数据, 按全量模式运行)")
        return {}

    latest = json_files[0]
    print(f"  加载历史: {latest.name}")
    with open(latest, encoding="utf-8") as f:
        data = json.load(f)

    posts = data.get("posts", [])
    return {p["post_id"]: p for p in posts}


# ── 列表页爬取 (增量/全量) ─────────────────────────────

def scrape_listing_pages(max_pages=200, known_ids=None):
    """
    翻页爬取帖子列表。
    增量模式: 当一整页所有帖子都在 known_ids 中且超过 INCREMENTAL_WINDOW_DAYS → 停止。
    """
    posts = []
    stop_date = datetime.now() - timedelta(days=MAX_AGE_DAYS)
    known_ids = known_ids or set()
    stopped_early = False

    for page in range(1, max_pages + 1):
        url = f"{BASE_URL}/page/{page}" if page > 1 else BASE_URL
        print(f"  列表 第{page}页...", end=" ", flush=True)

        try:
            resp = SESSION.get(url, timeout=20)
            resp.encoding = "utf-8"
            html = resp.text
        except Exception as e:
            print(f"✗ {e}")
            break

        entries = re.finditer(
            r'<article[^>]*>.*?href="(https://game\.xsharing\.cc/(\d+)\.html)".*?</article>',
            html, re.DOTALL,
        )

        page_posts = []
        all_known = True
        newest_known_date = None

        for entry in entries:
            block = entry.group(0)
            post_id = entry.group(2)
            post_url = entry.group(1)

            title_m = re.search(r"<h[23][^>]*>(.*?)</h[23]>", block, re.DOTALL)
            title = re.sub(r"<[^>]+>", "", title_m.group(1)).strip() if title_m else ""

            cat_m = re.search(r'<a[^>]*category[^>]*>(.*?)</a>', block)
            category = cat_m.group(1).strip() if cat_m else ""

            date_obj = extract_date(block)

            # 超过 90 天的跳过
            if date_obj and date_obj < stop_date:
                continue

            is_known = post_id in known_ids

            page_post = {
                "post_id": post_id,
                "url": post_url,
                "title": title[:120],
                "category": category,
                "date": date_obj.strftime("%Y-%m-%d") if date_obj else "",
                "date_obj": date_obj,
            }
            page_posts.append(page_post)

            if not is_known:
                all_known = False
            elif date_obj and (newest_known_date is None or date_obj > newest_known_date):
                newest_known_date = date_obj

        posts.extend(page_posts)
        new_count = sum(1 for p in page_posts if p["post_id"] not in known_ids)
        print(f"{len(page_posts)}条 (新:{new_count})")

        # 增量模式停止条件: 整页都是已知帖子
        if known_ids and all_known and page_posts:
            # 检查这页已知帖子的日期是否都超过 7 天（确保没有漏掉新帖）
            if newest_known_date:
                days_ago = (datetime.now() - newest_known_date).days
                if days_ago >= INCREMENTAL_WINDOW_DAYS:
                    print(f"  → 整页已知且最早 {days_ago} 天前, 停止翻页")
                    stopped_early = True
                    break
            else:
                # 有已知帖子但没日期, 保守继续
                pass

        if len(page_posts) == 0:
            print("  无更多帖子, 停止")
            break

        # 每页去重 (同一页可能出现重复)
        seen = set()
        deduped = []
        for p in posts:
            if p["post_id"] not in seen:
                seen.add(p["post_id"])
                deduped.append(p)
        posts = deduped

        time.sleep(0.5)

    # 最后过滤: 只保留 90 天内的
    recent = [p for p in posts if p.get("date_obj") and p["date_obj"] >= stop_date]
    print(f"\n  列表总数: {len(posts)} | 90天内: {len(recent)}"
          f"{' | 增量停止' if stopped_early else ''}")
    return recent


# ── 详情页爬取 ────────────────────────────────────────

def scrape_detail(post, retries=2):
    """爬取详情页, 提取解锁下载数等"""
    for attempt in range(retries):
        try:
            resp = SESSION.get(post["url"], timeout=15)
            resp.encoding = "utf-8"
            html = resp.text
            break
        except Exception as e:
            if attempt == retries - 1:
                print(f"    ✗ {e}")
                return None
            time.sleep(2)

    # 解锁下载数: "已有...X...人解锁下载"
    dl_m = re.search(r"已有.*?(\d+).*?人解锁下载", html)
    downloads = int(dl_m.group(1)) if dl_m else 0

    # 浏览量
    views_m = re.search(r'(\d+(?:\.\d+)?[Kk]?)\s*次?(?:查看|浏览|阅读)', html)
    views = views_m.group(1) if views_m else ""

    # 点赞数
    likes_m = re.search(r"(\d+)\s*人点赞", html)
    likes = int(likes_m.group(1)) if likes_m else 0

    # 评论数
    comments_m = re.search(r"(\d+)\s*条评论", html)
    comments = int(comments_m.group(1)) if comments_m else 0

    # 内容摘要
    content_m = re.search(
        r'class="entry-content[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL
    )
    excerpt = ""
    if content_m:
        text = re.sub(r"<[^>]+>", " ", content_m.group(1))
        text = re.sub(r"\s+", " ", text)
        excerpt = text.strip()[:300]

    return {
        **post,
        "downloads": downloads,
        "views": views,
        "likes": likes,
        "comments": comments,
        "excerpt": excerpt,
    }


# ── 输出 ──────────────────────────────────────────────

def save_output(details, today):
    """保存 JSON + Markdown, 同步到 Wiki"""
    details.sort(key=lambda x: x["downloads"], reverse=True)

    out = {k: v for d in details for k, v in d.items() if k != "date_obj"}

    clean = [
        {k: v for k, v in d.items() if k != "date_obj"}
        for d in details
    ]

    # JSON
    json_path = OUTPUT_DIR / f"xsharing-{today}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "source": "xsharing.org",
                "date": today,
                "total": len(clean),
                "posts": clean,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )
    print(f"  ✓ JSON: {json_path} ({len(clean)} 篇)")

    # Markdown
    md_path = OUTPUT_DIR / f"xsharing-{today}.md"
    lines = [
        f"# Xsharing — 近半年帖子 (按解锁下载排序)",
        "",
        f"> 更新时间: {today} | 总数: {len(clean)} 篇",
        "",
        "| # | 解锁 | 标题 | 分类 | 日期 |",
        "|---|------|------|------|------|",
    ]
    for i, d in enumerate(clean[:50], 1):
        title = d["title"][:40]
        lines.append(
            f"| {i} | {d['downloads']} | [{title}]({d['url']}) | {d['category']} | {d['date']} |"
        )

    lines.append("")
    lines.append("---")
    lines.append("")
    for i, d in enumerate(clean[:20], 1):
        lines.append(f"## {i}. {d['title']} ({d['downloads']}人解锁)")
        lines.append(
            f"- 分类: {d['category']} | 日期: {d['date']} | "
            f"浏览: {d['views']} | 点赞: {d['likes']} | 评论: {d['comments']}"
        )
        lines.append(f"- 链接: {d['url']}")
        if d.get("excerpt"):
            lines.append(f"- 摘要: {d['excerpt'][:200]}...")
        lines.append("")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  ✓ Markdown: {md_path}")

    # 同步到 Obsidian Wiki
    wiki_path = WIKI_DIR / f"xsharing-排行-{today}.md"
    with open(wiki_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  ✓ Wiki: {wiki_path}")

    return json_path, md_path


# ── 主流程 ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-pages", type=int, default=500, help="最大翻页数")
    parser.add_argument("--limit", type=int, default=0, help="限制抓取详情数(0=全部)")
    parser.add_argument(
        "--incremental", action="store_true", help="增量模式: 只抓新帖 + 刷新 Top N"
    )
    parser.add_argument(
        "--refresh-top", type=int, default=REFRESH_TOP_N, help="刷新已有 Top N 下载量"
    )
    args = parser.parse_args()

    today = datetime.now().strftime("%Y-%m-%d")
    mode_label = "增量" if args.incremental else "全量"
    print(f"Xsharing 爬虫 [{mode_label}] — {today}")
    print(f"{'='*50}")

    # ── 加载历史 ──
    previous = {}
    if args.incremental:
        previous = load_previous_results()
        print(f"  历史收录: {len(previous)} 篇")
    known_ids = set(previous.keys())

    # ── Phase 1: 列表 ──
    print(f"\n[1/3] 爬取帖子列表...")
    posts = scrape_listing_pages(args.max_pages, known_ids=known_ids)
    new_posts = [p for p in posts if p["post_id"] not in known_ids]
    print(f"  新增: {len(new_posts)} 篇 | 待抓详情: {len(posts)} 篇")

    # ── Phase 2: 详情 (新帖 + 刷新) ──
    print(f"\n[2/3] 爬取详情页...")

    # 2a: 新帖详情
    all_details = dict(previous)  # 从历史数据开始
    todo_new = new_posts[: args.limit] if args.limit else new_posts
    BATCH = 200

    if todo_new:
        print(f"\n  --- 新帖详情 ({len(todo_new)} 篇) ---")
        for batch_start in range(0, len(todo_new), BATCH):
            batch_end = min(batch_start + BATCH, len(todo_new))
            batch = todo_new[batch_start:batch_end]
            print(f"  批次 [{batch_start+1}-{batch_end}]...")
            for i, p in enumerate(batch):
                idx = batch_start + i + 1
                print(f"    [{idx}/{len(todo_new)}] {p['title'][:40]}...", end=" ", flush=True)
                detail = scrape_detail(p)
                if detail:
                    all_details[detail["post_id"]] = detail
                    print(f"✓ {detail['downloads']}人")
                else:
                    # 保留列表信息, 下载量标 0
                    all_details[p["post_id"]] = {**p, "downloads": 0, "views": "", "likes": 0, "comments": 0, "excerpt": ""}
                    print("✗")
                time.sleep(0.3)
            print(f"  批次完成, 累计: {len(all_details)} 篇")
    else:
        print("  (无新帖)")

    # 2b: 刷新已有 Top N 下载量
    if args.incremental and args.refresh_top > 0:
        existing = sorted(
            [d for d in all_details.values()],
            key=lambda x: x.get("downloads", 0),
            reverse=True,
        )
        to_refresh = existing[: args.refresh_top]
        print(f"\n  --- 刷新 Top {len(to_refresh)} 下载量 ---")
        refreshed = 0
        changed = 0
        for i, d in enumerate(to_refresh):
            old_dl = d.get("downloads", 0)
            print(f"    [{i+1}/{len(to_refresh)}] {d['title'][:40]}...", end=" ", flush=True)
            detail = scrape_detail(d)
            if detail:
                new_dl = detail.get("downloads", 0)
                if new_dl != old_dl:
                    changed += 1
                all_details[detail["post_id"]] = detail
                refreshed += 1
                print(f"✓ {old_dl}→{new_dl}")
            else:
                print("✗")
            time.sleep(0.3)
        print(f"  刷新完成: {refreshed} 篇, {changed} 篇有变化")

    # ── Phase 3: 过滤 & 排序 & 输出 ──
    print(f"\n[3/3] 排序 & 输出...")
    details = list(all_details.values())

    # 过滤: 只保留有下载量 > 0 或 90天内的
    stop_date = datetime.now() - timedelta(days=MAX_AGE_DAYS)

    def keep(d):
        if d.get("downloads", 0) > 0:
            return True
        # 从 date 字段判断
        try:
            dt = datetime.strptime(d.get("date", ""), "%Y-%m-%d")
            return dt >= stop_date
        except ValueError:
            return False

    details = [d for d in details if keep(d)]
    print(f"  过滤后: {len(details)} 篇")

    save_output(details, today)

    # ── 摘要 ──
    print(f"\n{'='*50}")
    print(f"Top 10 解锁下载:")
    for i, d in enumerate(details[:10], 1):
        print(f"  {i:2}. [{d['downloads']:4}人] {d['title'][:50]} ({d['date']})")


if __name__ == "__main__":
    main()
