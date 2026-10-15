#!/usr/bin/env python3
"""Scrape a list of public best-practice pages, extract readable text."""
import subprocess, re, html, sys, os

URLS = {
    "anthropic_effective_agents": "https://www.anthropic.com/engineering/building-effective-agents",
    "mcp": "https://modelcontextprotocol.io/",
    "a2a": "https://a2a-protocol.org/",
    "salesforce_agentforce": "https://www.salesforce.com/agentforce/",
    "ms_copilot_studio": "https://learn.microsoft.com/en-us/microsoft-copilot-studio/fundamentals-what-is-copilot-studio",
}

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
OUT = "/root/ClaudeProjects/SSG_AI/SSG_Sales_AI_Blueprint/references/scrape"
os.makedirs(OUT, exist_ok=True)

def fetch(url):
    try:
        r = subprocess.run(
            ["curl", "-sL", "--max-time", "30", "-A", UA, url],
            capture_output=True, text=True, timeout=35,
        )
        return r.stdout
    except Exception as e:
        return f"ERROR: {e}"

def extract_text(html_text):
    # remove scripts/styles
    h = re.sub(r"<script[^>]*>.*?</script>", " ", html_text, flags=re.S | re.I)
    h = re.sub(r"<style[^>]*>.*?</style>", " ", h, flags=re.S | re.I)
    h = re.sub(r"<noscript[^>]*>.*?</noscript>", " ", h, flags=re.S | re.I)
    # insert newlines for block elements
    h = re.sub(r"(?i)<(p|div|li|h[1-6]|tr|br|section|article)[^>]*>", "\n", h)
    h = re.sub(r"(?i)</(p|div|li|h[1-6]|tr|section|article)>", "\n", h)
    # strip remaining tags
    h = re.sub(r"<[^>]+>", " ", h)
    h = html.unescape(h)
    # collapse whitespace
    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in h.split("\n")]
    lines = [ln for ln in lines if len(ln) > 1]
    # dedupe consecutive duplicates
    out = []
    for ln in lines:
        if not out or out[-1] != ln:
            out.append(ln)
    return "\n".join(out)

for name, url in URLS.items():
    print(f"\n{'#'*60}\n# {name}: {url}\n{'#'*60}", flush=True)
    raw = fetch(url)
    txt = extract_text(raw)
    txt = txt[:8000]
    with open(f"{OUT}/{name}.txt", "w") as f:
        f.write(txt)
    print(txt[:2000])
    print(f"... [saved {len(txt)} chars to {name}.txt]")
