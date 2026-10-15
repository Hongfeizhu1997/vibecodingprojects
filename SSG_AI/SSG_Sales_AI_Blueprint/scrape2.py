#!/usr/bin/env python3
import subprocess, re, html, os

URLS = {
    "anthropic_effective_agents_full": "https://www.anthropic.com/engineering/building-effective-agents",
    "a2a_latest": "https://a2a-protocol.org/latest/",
    "salesforce_how_it_works": "https://www.salesforce.com/agentforce/how-agentforce-works/",
    "anthropic_multi_agent": "https://www.anthropic.com/engineering/multi-agent-research-system",
    "ms_agents_overview": "https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-overview",
}

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
OUT = "/root/ClaudeProjects/SSG_AI/SSG_Sales_AI_Blueprint/references/scrape"
os.makedirs(OUT, exist_ok=True)

def fetch(url):
    try:
        r = subprocess.run(["curl", "-sL", "--max-time", "30", "-A", UA, url],
                           capture_output=True, text=True, timeout=35)
        return r.stdout
    except Exception as e:
        return f"ERROR: {e}"

def extract_text(h):
    h = re.sub(r"<script[^>]*>.*?</script>", " ", h, flags=re.S | re.I)
    h = re.sub(r"<style[^>]*>.*?</style>", " ", h, flags=re.S | re.I)
    h = re.sub(r"<noscript[^>]*>.*?</noscript>", " ", h, flags=re.S | re.I)
    h = re.sub(r"(?i)<(p|div|li|h[1-6]|tr|br|section|article)[^>]*>", "\n", h)
    h = re.sub(r"(?i)</(p|div|li|h[1-6]|tr|section|article)>", "\n", h)
    h = re.sub(r"<[^>]+>", " ", h)
    h = html.unescape(h)
    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in h.split("\n")]
    lines = [ln for ln in lines if len(ln) > 1]
    out = []
    for ln in lines:
        if not out or out[-1] != ln:
            out.append(ln)
    return "\n".join(out)

for name, url in URLS.items():
    print(f"\n{'#'*50}\n# {name}: {url}", flush=True)
    raw = fetch(url)
    txt = extract_text(raw)
    txt = txt[:25000]
    with open(f"{OUT}/{name}.txt", "w") as f:
        f.write(txt)
    print(f"[saved {len(txt)} chars]")
