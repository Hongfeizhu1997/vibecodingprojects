#!/usr/bin/env python3
"""
TopSecret - xlbbbs.com 热帖爬取 + 人物/店铺实体合并
用法: python3 main.py                    # 全部城市
      python3 main.py --city tianjin     # 单个城市
"""

import re
import json
import time
import hashlib
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

import requests
import yaml
from bs4 import BeautifulSoup

# ── 配置加载 ──────────────────────────────────────────

BASE_DIR = Path(__file__).parent
with open(BASE_DIR / "config.yaml") as f:
    CONFIG = yaml.safe_load(f)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
}
SESSION = requests.Session()
SESSION.headers.update(HEADERS)

# ── 工具函数 ──────────────────────────────────────────

def fetch(url, retries=3):
    """带重试的 HTTP GET"""
    for i in range(retries):
        try:
            resp = SESSION.get(url, timeout=CONFIG["scraper"]["timeout"])
            resp.encoding = "utf-8"
            return resp.text
        except Exception as e:
            if i == retries - 1:
                print(f"  ✗ 请求失败 {url}: {e}")
                return None
            time.sleep(2)

def parse_date(date_str):
    """解析日期字符串: '2025-8-13' 或 '2025-8-13 19:28'"""
    if not date_str:
        return None
    date_str = date_str.strip()
    for fmt in ["%Y-%m-%d %H:%M", "%Y-%m-%d", "%Y-%m-%d %H:%M:%S"]:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    # 相对日期: "昨天15:31", "16小时前", "3天前"
    now = datetime.now()
    if "小时前" in date_str:
        hours = int(re.search(r"(\d+)", date_str).group(1))
        return now - timedelta(hours=hours)
    if "昨天" in date_str:
        return now - timedelta(days=1)
    if "天前" in date_str:
        days = int(re.search(r"(\d+)", date_str).group(1))
        return now - timedelta(days=days)
    if "前天" in date_str:
        return now - timedelta(days=2)
    return None

def is_recent(date_obj, max_age_days=90):
    """判断日期是否在 N 天内"""
    if date_obj is None:
        return False
    return (datetime.now() - date_obj).days <= max_age_days

def clean_html(text):
    """去除 HTML 标签，保留纯文本"""
    if not text:
        return ""
    text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.DOTALL)
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def text_similarity(a, b):
    """简单的 Jaccard 相似度（基于 2-gram 字符）"""
    if not a or not b:
        return 0.0
    def ngrams(s, n=2):
        return set(s[i:i+n] for i in range(len(s)-n+1))
    set_a = ngrams(a)
    set_b = ngrams(b)
    if not set_a or not set_b:
        return 0.0
    return len(set_a & set_b) / len(set_a | set_b)

# ── Phase 1: 爬取帖子列表 ──────────────────────────────

def scrape_thread_list(fid, path_tpl, mode_name, max_pages=2):
    """爬取指定版块的帖子列表（热帖/最新等）"""
    threads = []
    base = CONFIG["scraper"]["base_url"]

    for page in range(1, max_pages + 1):
        url = f"{base}/{path_tpl.format(fid=fid)}"
        if page > 1:
            url += f"&page={page}"

        print(f"    [{mode_name}] 第{page}页: {url}")
        html = fetch(url)
        if not html:
            continue

        soup = BeautifulSoup(html, "lxml")
        page_threads = 0

        for tbody in soup.find_all("tbody", id=re.compile(r"normalthread_\d+")):
            tid = tbody.get("id", "").replace("normalthread_", "")

            # 标题 + URL
            title_tag = tbody.find("a", class_="xst")
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            thread_url = title_tag.get("href", "")
            if thread_url and not thread_url.startswith("http"):
                thread_url = base + "/" + thread_url

            # 区域标签 [海淀] [丰台] 等
            district_tag = tbody.find("em")
            district = ""
            if district_tag:
                district_link = district_tag.find("a")
                if district_link:
                    district = district_link.get_text(strip=True)

            # 热度
            heat_tag = tbody.find("img", alt="heatlevel")
            heat = 0
            if heat_tag and heat_tag.get("title"):
                heat_m = re.search(r"(\d+)", heat_tag["title"])
                if heat_m:
                    heat = int(heat_m.group(1))

            # 作者 + 发布时间
            author_span = tbody.find("p", class_="author")
            author = ""
            post_date = None
            if author_span:
                spans = author_span.find_all("span")
                for span in spans:
                    text = span.get_text(strip=True)
                    if "发布于" in text:
                        author = text.replace("发布于", "").strip()
                    elif re.match(r"\d{4}-\d", text):
                        post_date = parse_date(text)

            # 浏览/回复
            views = 0
            replies = 0
            info_p = tbody.find("p", class_="y")
            if info_p:
                info_text = info_p.get_text()
                v_m = re.search(r"浏览\D*(\d+)", info_text)
                r_m = re.search(r"回复\D*(\d+)", info_text)
                if v_m:
                    views = int(v_m.group(1))
                if r_m:
                    replies = int(r_m.group(1))

            # 是否有图
            has_image = bool(tbody.find("img", alt="attach_img"))

            threads.append({
                "thread_id": tid,
                "title": title,
                "url": thread_url,
                "district": district,
                "author": author,
                "post_date": post_date.strftime("%Y-%m-%d") if post_date else "",
                "post_date_obj": post_date,
                "views": views,
                "replies": replies,
                "heat": heat,
                "has_image": has_image,
            })
            page_threads += 1

        print(f"    获取 {page_threads} 条")

        if page_threads == 0:
            break

    return threads

# ── Phase 2: 爬取详情页 ────────────────────────────────

def scrape_thread_detail(thread):
    """爬取单个帖子详情"""
    url = thread["url"]
    html = fetch(url)
    if not html:
        return None

    soup = BeautifulSoup(html, "lxml")

    # 楼主内容
    content = ""
    t_f = soup.find("td", class_="t_f")
    if t_f:
        content = clean_html(str(t_f))

    # 体验报告 (caption 标签内)
    report = {}
    report_caption = soup.find("caption", string="体验报告")
    report_table = report_caption.find_parent("table") if report_caption else None
    if report_table:
        for row in report_table.find_all("tr"):
            th = row.find("th")
            td = row.find("td")
            if th and td:
                key = th.get_text(strip=True).rstrip(":")
                val = clean_html(str(td))
                # 排除付费/隐藏内容
                if "金币" in val or "回复后查看" in val or "登录" in val:
                    val = "[需付费]"
                report[key] = val

    # 发布日期（精确到分钟）
    date_fine = thread.get("post_date", "")
    date_tag = soup.find("em", string=re.compile(r"发表于"))
    if date_tag:
        date_text = date_tag.get_text()
        d = parse_date(date_text)
        if d:
            date_fine = d.strftime("%Y-%m-%d %H:%M")

    # 图片数
    image_count = 0
    picnum = soup.find("em", class_="picnum")
    if picnum:
        pic_text = picnum.get_text()
        n = re.search(r"(\d+)", pic_text)
        if n:
            image_count = int(n.group(1))

    return {
        **thread,
        "content": content[:2000],  # 截断过长内容
        "report": report,
        "post_date": date_fine,
        "image_count": image_count,
    }

# ── Phase 3: 实体提取 ──────────────────────────────────

def extract_entity(detail):
    """从帖子详情提取人物/店铺实体"""
    report = detail.get("report", {})
    title = detail.get("title", "")
    content = detail.get("content", "")

    # 实体名称：优先从标题提取
    entity_name = title
    # 尝试去除区标签
    entity_name = re.sub(r"^\s*\[.*?\]\s*", "", entity_name).strip()

    # 地址
    address = report.get("详细地址", "")

    # 类型判断
    entity_type = "person"
    shop_keywords = ["店", "会所", "洗浴", "足疗", "养生", "SPA", "spa", "按摩店", "工作室"]
    if any(kw in title or kw in content for kw in shop_keywords):
        entity_type = "shop"

    # 特征提取
    features = {
        "name": entity_name,
        "type": entity_type,
        "address": address,
        "age": report.get("妹子年龄", ""),
        "price": report.get("消费情况", ""),
        "services": report.get("服务项目", ""),
        "count": report.get("妹子数量", ""),
    }

    # 区分人/店的额外特征
    if entity_type == "person":
        # 从内容提取身体特征关键词
        body_keywords = []
        for kw in ["巨乳", "大胸", "翘臀", "苗条", "丰满", "高挑", "娇小", "白皙",
                    "少妇", "学生", "御姐", "萝莉", "熟女", "嫩模"]:
            if kw in title or kw in content:
                body_keywords.append(kw)
        features["body_type"] = " ".join(body_keywords)

    return {
        "entity_id": hashlib.md5(f"{entity_name}|{address}".encode()).hexdigest()[:12],
        "entity_name": entity_name,
        "entity_type": entity_type,
        "features": features,
        "source_threads": [{
            "thread_id": detail["thread_id"],
            "title": detail["title"],
            "url": detail["url"],
            "post_date": detail["post_date"],
            "views": detail["views"],
            "heat": detail["heat"],
            "excerpt": content[:300],
        }],
        "last_seen": detail["post_date"],
        "first_seen": detail["post_date"],
        "thread_count": 1,
        "total_views": detail["views"],
    }

# ── Phase 4: 实体合并 ──────────────────────────────────

def merge_entities(entities):
    """合并同一人物/店铺的多个帖子"""
    merged = {}
    sim_threshold = CONFIG["merger"]["title_similarity"]

    for entity in entities:
        matched = False

        for eid, existing in merged.items():
            # 规则1: 相同地址 + 年龄接近 → 同一实体
            addr1 = entity["features"].get("address", "")
            addr2 = existing["features"].get("address", "")
            age1 = entity["features"].get("age", "")
            age2 = existing["features"].get("age", "")

            same_address = addr1 and addr2 and (addr1 == addr2 or addr1 in addr2 or addr2 in addr1)
            same_age = age1 and age2 and age1 == age2

            if same_address:
                matched = True
            elif same_address and same_age:
                matched = True
            # 规则2: 标题相似度高
            elif text_similarity(entity["entity_name"], existing["entity_name"]) > sim_threshold:
                matched = True

            if matched:
                # 合并
                entity_id = eid
                existing["source_threads"].extend(entity["source_threads"])
                existing["thread_count"] += 1
                existing["total_views"] += entity["total_views"]
                # 更新最后活跃时间
                if entity["last_seen"] > existing["last_seen"]:
                    existing["last_seen"] = entity["last_seen"]
                # 合并特征（不覆盖已有信息，优先保留有值的）
                for k, v in entity["features"].items():
                    if v and not existing["features"].get(k):
                        existing["features"][k] = v
                break

        if not matched:
            merged[entity["entity_id"]] = entity

    return list(merged.values())

# ── Phase 5: 输出 ──────────────────────────────────────

def generate_summary(city_name, merged_entities):
    """生成 Markdown 摘要"""
    lines = [f"# {city_name} — 热帖汇总", "",
             f"更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
             f"实体数: {len(merged_entities)} 个 (人物/店铺)",
             ""]

    # 按最近活跃排序
    sorted_entities = sorted(merged_entities,
                             key=lambda e: e["last_seen"], reverse=True)

    for e in sorted_entities:
        f = e["features"]
        name = e["entity_name"]
        addr = f.get("address", "未知地址")
        etype = "🏪 店铺" if e["entity_type"] == "shop" else "👤 个人"
        age = f.get("age", "")
        price = f.get("price", "")
        services = f.get("services", "")
        body = f.get("body_type", "")

        lines.append(f"## {name}")
        lines.append(f"- **{etype}** | 📍 {addr} | 最近活跃: {e['last_seen']}")
        if age:
            lines.append(f"- 年龄: {age}")
        if price:
            lines.append(f"- 价格: {price}")
        if body:
            lines.append(f"- 特征: {body}")
        if services:
            lines.append(f"- 服务: {services}")
        lines.append(f"- 帖子数: {e['thread_count']} | 总浏览: {e['total_views']}")

        # 帖子摘要
        if e["thread_count"] > 1:
            lines.append("")
            lines.append("**相关帖子:**")
        for t in e["source_threads"]:
            lines.append(f"  - [{t['title']}]({t['url']}) ({t['post_date']}, {t['views']}次浏览)")
            if t.get("excerpt"):
                lines.append(f"    > {t['excerpt'][:150]}...")

        lines.append("")

    return "\n".join(lines)

def save_output(city_name, threads, entities, keep_history=True):
    """保存 JSON 和 Markdown（含历史版本）"""
    output_dir = BASE_DIR / CONFIG["output"]["dir"]
    output_dir.mkdir(exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")

    # 历史版本目录
    history_dir = output_dir / "history"
    history_dir.mkdir(exist_ok=True)

    # JSON — 最新版
    json_path = output_dir / f"{city_name}.json"
    json_data = {
        "city": city_name,
        "total_threads": len(threads),
        "total_entities": len(entities),
        "updated": datetime.now().isoformat(),
        "entities": entities,
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    print(f"  ✓ JSON (最新): {json_path}")

    # JSON — 历史版本
    if keep_history:
        hist_json = history_dir / f"{city_name}-{today}.json"
        with open(hist_json, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

    # Markdown — 最新版
    md_path = output_dir / f"{city_name}.md"
    summary = generate_summary(city_name, entities)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(summary)
    print(f"  ✓ Markdown (最新): {md_path}")

    # Markdown — 历史版本
    if keep_history:
        hist_md = history_dir / f"{city_name}-{today}.md"
        with open(hist_md, "w", encoding="utf-8") as f:
            f.write(summary)

    return json_path, md_path

def clean_old_history(days=90):
    """清理超过 N 天的历史版本"""
    history_dir = BASE_DIR / CONFIG["output"]["dir"] / "history"
    if not history_dir.exists():
        return

    cutoff = datetime.now() - timedelta(days=days)
    deleted = 0
    for f in history_dir.glob("*"):
        m = re.match(r".*-(\d{4}-\d{2}-\d{2})\.(json|md)$", f.name)
        if m:
            try:
                file_date = datetime.strptime(m.group(1), "%Y-%m-%d")
                if file_date < cutoff:
                    f.unlink()
                    deleted += 1
            except ValueError:
                pass
    if deleted:
        print(f"  ♻ 清理 {deleted} 个过期历史文件 (>{days}天)")

# ── 主流程 ──────────────────────────────────────────────

def run_city(city_key, max_pages=None):
    """跑单个城市全流程"""
    city = CONFIG["cities"].get(city_key)
    if not city:
        print(f"未知城市: {city_key}")
        return

    fid = city["fid"]
    name = city["name"]
    max_age = CONFIG["scraper"]["max_age_days"]
    if max_pages is None:
        max_pages = CONFIG["scraper"]["max_pages"]

    print(f"\n{'='*60}")
    print(f"  {name} (fid={fid})")
    print(f"{'='*60}")

    # Phase 1: 爬取列表（热帖 + 最新 双通道）
    print(f"\n[1/4] 爬取帖子列表...")
    all_threads = {}  # 用 thread_id 去重
    for mode in CONFIG["scraper"]["modes"]:
        print(f"  ── {mode['name']}模式 ──")
        threads = scrape_thread_list(fid, mode["path"], mode["name"], max_pages)
        for t in threads:
            tid = t["thread_id"]
            if tid not in all_threads or t.get("views", 0) > all_threads[tid].get("views", 0):
                all_threads[tid] = t
    threads = list(all_threads.values())
    print(f"  双通道合并: {len(threads)} 条（去重后）")

    # 浏览量过滤
    min_views = CONFIG["scraper"].get("min_views", 0)
    threads = [t for t in threads if t.get("views", 0) >= min_views]
    print(f"  浏览量≥{min_views}: {len(threads)} 条")

    # 日期过滤
    recent = [t for t in threads if t.get("post_date_obj") and is_recent(t["post_date_obj"], max_age)]
    print(f"  3个月内: {len(recent)} 条 (过滤掉 {len(threads) - len(recent)} 条)")

    # Phase 2: 爬取详情
    print(f"\n[2/4] 爬取详情页...")
    details = []
    for i, t in enumerate(recent):
        print(f"  [{i+1}/{len(recent)}] {t['title'][:40]}...")
        detail = scrape_thread_detail(t)
        if detail:
            details.append(detail)
        time.sleep(0.5)  # 礼貌间隔

    print(f"  成功: {len(details)} 条")

    # Phase 3: 提取实体
    print(f"\n[3/4] 提取实体...")
    entities = [extract_entity(d) for d in details]
    print(f"  提取 {len(entities)} 个实体")

    # Phase 4: 合并
    merged = merge_entities(entities)
    print(f"  合并后: {len(merged)} 个实体 (去重 {len(entities) - len(merged)} 个)")

    # Phase 5: 输出
    print(f"\n[4/4] 生成输出...")
    json_path, md_path = save_output(city_key, threads, merged)

    # 打印摘要预览
    print(f"\n{'─'*60}")
    print(f"  {name} 摘要预览")
    print(f"{'─'*60}")
    print(generate_summary(name, merged)[:2000])

    return merged

def main():
    parser = argparse.ArgumentParser(description="TopSecret - xlbbbs 爬虫")
    parser.add_argument("--city", type=str, help="只跑指定城市 (beijing/tianjin/shanghai/sichuan)")
    parser.add_argument("--pages", type=int, default=None, help="最大爬取页数")
    args = parser.parse_args()

    cities_to_run = [args.city] if args.city else list(CONFIG["cities"].keys())

    for city_key in cities_to_run:
        run_city(city_key, args.pages)

    # 汇总
    if not args.city:
        print(f"\n{'='*60}")
        print("  全部完成！输出文件在 output/ 目录下")
        print(f"{'='*60}")

    # 清理过期历史(>90天)
    clean_old_history(90)

if __name__ == "__main__":
    main()
