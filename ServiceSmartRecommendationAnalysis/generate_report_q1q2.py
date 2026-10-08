#!/usr/bin/env python3
"""
Generate SSR Phase 1 Operational KPI reports (Q1 and Q2) from contract CSV JSON.

Reads data/phase1_q1.json, phase1_q2.json, term_type_q1.json, term_type_q2.json
and emits two self-contained HTML reports reusing the established CSS framework.
"""
import json
from pathlib import Path

DATA = Path(__file__).resolve().parent / "data"
OUT = Path(__file__).resolve().parent / "validation_output"

GEO_ORDER = ['EMEA', 'AP', 'LA', 'NA']
TERM_ORDER = ['1Y', '2Y', '3Y', '4Y', '5Y']
TYPE_ORDER = ['Premier Support', 'Premier Support Plus', 'Onsite', 'Depot / Mail-in', 'Other / Add-on']

CSS = """<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',Arial,sans-serif;background:#f0f2f5;color:#222;font-size:14px}
.navbar{background:#1a237e;color:#fff;padding:12px 24px;display:flex;align-items:center;gap:16px;position:sticky;top:0;z-index:100;box-shadow:0 2px 8px rgba(0,0,0,.35);flex-wrap:wrap}
.navbar .brand{font-weight:700;font-size:15px}
.navbar a{color:#bbdefb;text-decoration:none;padding:4px 10px;border-radius:4px;font-size:12px}
.navbar a:hover{background:rgba(255,255,255,.15);color:#fff}
.page{max-width:1320px;margin:0 auto;padding:20px 24px}
.section{background:#fff;border-radius:8px;box-shadow:0 1px 4px rgba(0,0,0,.1);margin-bottom:24px;overflow:hidden}
.sec-hdr{background:#1a237e;color:#fff;padding:13px 20px}
.sec-hdr h2{font-size:17px;font-weight:600}
.sec-body{padding:18px 20px}
.sub{margin-bottom:22px}.sub:last-child{margin-bottom:0}
.sub h3{font-size:14px;font-weight:600;color:#37474f;margin-bottom:10px;border-left:4px solid #42a5f5;padding-left:10px}
.sub h4{font-size:13px;font-weight:600;color:#555;margin:14px 0 8px}
.insight{background:#e3f2fd;border-left:4px solid #1976d2;padding:9px 13px;border-radius:4px;font-size:13px;color:#0d47a1;margin-bottom:10px;line-height:1.5}
.warn{background:#fff3e0;border-left:4px solid #f57c00;padding:9px 13px;border-radius:4px;font-size:13px;color:#bf360c;margin-bottom:10px;line-height:1.5}
.critical{background:#ffebee;border-left:4px solid #c62828;padding:9px 13px;border-radius:4px;font-size:13px;color:#b71c1c;margin-bottom:10px;line-height:1.5}
table{border-collapse:collapse;width:100%;font-size:13px}
th{background:#37474f;color:#fff;padding:7px 10px;text-align:left;font-weight:600;white-space:nowrap}
td{padding:6px 10px;border-bottom:1px solid #eee;vertical-align:middle}
tr:last-child td{border-bottom:none}
.num{text-align:right;font-family:'Courier New',monospace;white-space:nowrap}
.kpi-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:20px}
.kpi-card{background:#f5f7ff;border:1px solid #e8eaf6;border-radius:8px;padding:14px}
.kpi-card .geo-tag{display:inline-block;background:#1a237e;color:#fff;border-radius:4px;padding:2px 8px;font-size:11px;font-weight:700;margin-bottom:6px}
.kpi-card .label{font-size:11px;color:#666;text-transform:uppercase;letter-spacing:.5px}
.kpi-card .big{font-size:24px;font-weight:700;margin:3px 0}
.kpi-card .sub{font-size:11px;color:#888;line-height:1.4;margin:0}
.legend{display:flex;gap:10px;font-size:11px;margin-bottom:8px;align-items:center}
.legend span{padding:2px 8px;border-radius:10px;color:#fff;font-weight:600}
.tag{display:inline-block;padding:1px 6px;border-radius:3px;font-size:11px;font-weight:600}
.tag-new{background:#e3f2fd;color:#1565c0}
.tag-copied{background:#e8f5e9;color:#2e7d32}
.tag-mtm{background:#fff3e0;color:#e65100}
.trend-up{color:#2e7d32;font-weight:700}
.trend-down{color:#c62828;font-weight:700}
.trend-flat{color:#f57f17;font-weight:700}
</style>"""

# ---- color helpers ----
def c_acc(v):
    if v is None: return ''
    if v >= 55: return 'style="background:#2e7d32;color:#fff"'
    if v >= 40: return 'style="background:#f57f17;color:#fff"'
    return 'style="background:#c62828;color:#fff"'

def c_cov(v):
    if v is None: return ''
    if v >= 97: return 'style="background:#2e7d32;color:#fff"'
    if v >= 93: return 'style="background:#f57f17;color:#fff"'
    return 'style="background:#c62828;color:#fff"'

def c_af(v):
    if v is None: return ''
    if v <= 15: return 'style="background:#2e7d32;color:#fff"'
    if v <= 25: return 'style="background:#f57f17;color:#fff"'
    return 'style="background:#c62828;color:#fff"'

def fmt(n):
    return f"{n:,}"

def pct(v, sign=False):
    if v is None: return '—'
    if sign and v > 0: return f"+{v:.1f}"
    return f"{v:.1f}"

def delta(cur, prev):
    if prev is None: return None
    return round(cur - prev, 1)

def delta_html(d):
    if d is None: return '<td class="num">—</td>'
    if abs(d) < 0.05: cls = 'trend-flat'
    elif d > 0: cls = 'trend-up'
    else: cls = 'trend-down'
    return f'<td class="num {cls}">{pct(d, sign=True)}pp</td>'

# ---- section builders ----
def kpi_dashboard(geo, g, prev_g=None):
    rows = [
        ("Total Contracts", g['total'], None, prev_g['total'] if prev_g else None, '—'),
        ("Default Coverage", g['has_default'], g['coverage'], prev_g['coverage'] if prev_g else None, c_cov(g['coverage'])),
        ("Service Attach Rate", g['has_selected'], g['attach'], prev_g['attach'] if prev_g else None, ''),
        ("Acceptance Rate", g['accepted'], g['acceptance'], prev_g['acceptance'] if prev_g else None, c_acc(g['acceptance'])),
        ("Change Rate", g['changed'], g['change'], prev_g['change'] if prev_g else None, ''),
        ("Attachment Failure", None, g['attach_failure'], prev_g['attach_failure'] if prev_g else None, c_af(g['attach_failure'])),
        ("No Default", None, g['no_default'], None, ''),
    ]
    html = [f'<div class="sub"><h3>A. KPI Dashboard (n={fmt(g["total"])})</h3>',
            '<div class="legend"><span style="background:#2e7d32">Good</span><span style="background:#f57f17">Moderate</span><span style="background:#c62828">Needs attention</span></div>',
            '<table><tr><th>Metric</th><th class="num">Count</th><th class="num">Rate</th>']
    if prev_g: html.append('<th class="num">Q1 Rate</th><th class="num">Δ</th>')
    html.append('</tr>')
    for name, cnt, rate, prev_rate, style in rows:
        html.append(f'<tr><td>{name}</td>')
        html.append(f'<td class="num">{fmt(cnt) if cnt is not None else "—"}</td>')
        html.append(f'<td class="num" {style}>{pct(rate)}%</td>' if rate is not None else '<td class="num">—</td>')
        if prev_g:
            if name == "Total Contracts":
                html.append(f'<td class="num">{fmt(int(prev_rate)) if prev_rate is not None else "—"}</td>')
                html.append('<td class="num">—</td>')
            else:
                html.append(f'<td class="num">{pct(prev_rate)}%</td>' if prev_rate is not None else '<td class="num">—</td>')
                html.append(delta_html(delta(rate, prev_rate) if rate is not None and prev_rate is not None else None))
        html.append('</tr>')
    html.append('</table></div>')
    return '\n'.join(html)

def origin_section(geo, go):
    html = ['<div class="sub"><h3>B. KPI by Config Origin</h3>',
            '<table><tr><th>Origin</th><th class="num">Contracts</th><th class="num">Coverage</th><th class="num">Attach</th><th class="num">Acceptance</th><th class="num">Change</th><th class="num">Att.Fail</th></tr>']
    tags = {'New CTO': 'tag-new', 'Copied CTO': 'tag-copied', 'MTM': 'tag-mtm'}
    for o in ['New CTO', 'Copied CTO', 'MTM']:
        d = go.get(o)
        if not d: continue
        html.append(f'<tr><td><span class="tag {tags.get(o,"")}">{o}</span></td>'
                    f'<td class="num">{fmt(d["total"])}</td>'
                    f'<td class="num" {c_cov(d["coverage"])}>{d["coverage"]}%</td>'
                    f'<td class="num">{d["attach"]}%</td>'
                    f'<td class="num" {c_acc(d["acceptance"])}>{d["acceptance"]}%</td>'
                    f'<td class="num">{d["change"]}%</td>'
                    f'<td class="num" {c_af(d["attach_failure"])}>{d["attach_failure"]}%</td></tr>')
    html.append('</table></div>')
    return '\n'.join(html)

def source_section(geo, gs):
    html = ['<div class="sub"><h3>C. Default Source Acceptance (AI vs Non-AI vs ALL)</h3>',
            '<table><tr><th>Default Source</th><th class="num">Contracts</th><th class="num">Attach</th><th class="num">Acceptance</th><th class="num">Change</th><th class="num">Att.Fail</th></tr>']
    for s in ['AI', 'Non-AI', 'ALL']:
        d = gs.get(s)
        if not d: continue
        html.append(f'<tr><td><strong>{s}</strong></td>'
                    f'<td class="num">{fmt(d["total"])}</td>'
                    f'<td class="num">{d["attach"]}%</td>'
                    f'<td class="num" {c_acc(d["acceptance"])}>{d["acceptance"]}%</td>'
                    f'<td class="num">{d["change"]}%</td>'
                    f'<td class="num" {c_af(d["attach_failure"])}>{d["attach_failure"]}%</td></tr>')
    html.append('</table></div>')
    return '\n'.join(html)

def country_section(geo, cs, top=12):
    items = list(cs.items())[:top]
    html = [f'<div class="sub"><h3>D. Country Drill-Down (Top {len(items)})</h3>',
            '<table><tr><th>Country</th><th class="num">Contracts</th><th class="num">Coverage</th><th class="num">Acceptance</th><th class="num">Change</th><th class="num">Att.Fail</th></tr>']
    for c, d in items:
        html.append(f'<tr><td><strong>{c}</strong></td>'
                    f'<td class="num">{fmt(d["total"])}</td>'
                    f'<td class="num" {c_cov(d["coverage"])}>{d["coverage"]}%</td>'
                    f'<td class="num" {c_acc(d["acceptance"])}>{d["acceptance"]}%</td>'
                    f'<td class="num">{d["change"]}%</td>'
                    f'<td class="num" {c_af(d["attach_failure"])}>{d["attach_failure"]}%</td></tr>')
    html.append('</table></div>')
    return '\n'.join(html)

def monthly_section(geo, gm):
    html = ['<div class="sub"><h3>E. Monthly Trend</h3>',
            '<table><tr><th>Month</th><th class="num">Contracts</th><th class="num">Coverage</th><th class="num">Attach</th><th class="num">Acceptance</th><th class="num">Change</th><th class="num">Att.Fail</th></tr>']
    for m in sorted(gm.keys()):
        d = gm[m]
        html.append(f'<tr><td><strong>{m}</strong></td>'
                    f'<td class="num">{fmt(d["total"])}</td>'
                    f'<td class="num">{d["coverage"]}%</td>'
                    f'<td class="num">{d["attach"]}%</td>'
                    f'<td class="num" {c_acc(d["acceptance"])}>{d["acceptance"]}%</td>'
                    f'<td class="num">{d["change"]}%</td>'
                    f'<td class="num" {c_af(d["attach_failure"])}>{d["attach_failure"]}%</td></tr>')
    html.append('</table></div>')
    return '\n'.join(html)

def term_type_section(geo, tt):
    # tt[geo] = {term: {type: {...}}}
    geo_tt = tt.get(geo, {})
    # By Term (aggregate across types)
    term_agg = {}
    for term, types in geo_tt.items():
        tot = sum(c['total'] for c in types.values())
        acc = sum(c['total'] * c['acceptance'] for c in types.values())
        chg = sum(c['total'] * c['change'] for c in types.values())
        af = sum(c['total'] * c['att_fail'] for c in types.values())
        term_agg[term] = {'total': tot, 'acc': round(acc/tot,1) if tot else 0,
                          'chg': round(chg/tot,1) if tot else 0, 'af': round(af/tot,1) if tot else 0}
    # By Type (aggregate across terms)
    type_agg = {}
    for term, types in geo_tt.items():
        for typ, c in types.items():
            t = type_agg.setdefault(typ, {'total':0,'acc_s':0,'chg_s':0,'af_s':0})
            t['total'] += c['total']; t['acc_s'] += c['total']*c['acceptance']
            t['chg_s'] += c['total']*c['change']; t['af_s'] += c['total']*c['att_fail']

    html = ['<div class="sub"><h3>F. Service Product Analysis — Term × Type</h3>']
    html.append('<h4>By Term</h4><table><tr><th>Term</th><th class="num">Contracts</th><th class="num">Acceptance</th><th class="num">Change</th><th class="num">Att.Fail</th></tr>')
    for term in TERM_ORDER:
        d = term_agg.get(term)
        if not d or d['total'] == 0: continue
        html.append(f'<tr><td><strong>{term}</strong></td><td class="num">{fmt(d["total"])}</td>'
                    f'<td class="num" {c_acc(d["acc"])}>{d["acc"]}%</td>'
                    f'<td class="num">{d["chg"]}%</td>'
                    f'<td class="num" {c_af(d["af"])}>{d["af"]}%</td></tr>')
    html.append('</table>')
    html.append('<h4>By Type</h4><table><tr><th>Type</th><th class="num">Contracts</th><th class="num">Acceptance</th><th class="num">Change</th><th class="num">Att.Fail</th></tr>')
    for typ in TYPE_ORDER:
        t = type_agg.get(typ)
        if not t or t['total'] == 0: continue
        acc = round(t['acc_s']/t['total'],1); chg = round(t['chg_s']/t['total'],1); af = round(t['af_s']/t['total'],1)
        html.append(f'<tr><td><strong>{typ}</strong></td><td class="num">{fmt(t["total"])}</td>'
                    f'<td class="num" {c_acc(acc)}>{acc}%</td>'
                    f'<td class="num">{chg}%</td>'
                    f'<td class="num" {c_af(af)}>{af}%</td></tr>')
    html.append('</table></div>')
    return '\n'.join(html)

def cross_geo_product(tt):
    # aggregate acceptance by type across GEOs for comparison
    html = ['<div class="section" id="term-type-cross"><div class="sec-hdr"><h2>Cross-GEO Service Product Comparison</h2></div><div class="sec-body">',
            '<table><tr><th>Type</th>']
    for g in GEO_ORDER: html.append(f'<th class="num">{g} Accept.</th>')
    html.append('</tr>')
    for typ in TYPE_ORDER:
        html.append(f'<tr><td><strong>{typ}</strong></td>')
        for g in GEO_ORDER:
            geo_tt = tt.get(g, {})
            # aggregate across terms for this type
            tot = acc_s = 0
            for term, types in geo_tt.items():
                c = types.get(typ)
                if c: tot += c['total']; acc_s += c['total']*c['acceptance']
            if tot:
                a = round(acc_s/tot,1)
                html.append(f'<td class="num" {c_acc(a)}>{a}%</td>')
            else:
                html.append('<td class="num">—</td>')
        html.append('</tr>')
    html.append('</table></div></div>')
    return '\n'.join(html)

def exec_summary(kpi, prev=None):
    geo = kpi['geo']
    cards = []
    for g in GEO_ORDER:
        d = geo.get(g, {})
        if not d: continue
        acc = d['acceptance']
        color = {'style': ''}
        if acc >= 55: color = {'style': 'style="color:#2e7d32"'}
        elif acc < 40: color = {'style': 'style="color:#c62828"'}
        else: color = {'style': 'style="color:#f57f17"'}
        d_str = '' if not prev else f" (Q1: {prev['geo'].get(g,{}).get('acceptance','—')}%)"
        cards.append(f'<div class="kpi-card"><div class="geo-tag">{g}</div><div class="label">Acceptance Rate</div>'
                     f'<div class="big" {color["style"]}>{acc}%</div>'
                     f'<div class="sub">{fmt(d["total"])} contracts | {d["coverage"]}% coverage</div>'
                     f'<div class="sub">Attach: {d["attach"]}% | Change: {d["change"]}% | Att.Fail: {d["attach_failure"]}%</div></div>')
    return '\n'.join(cards)

def cross_geo_table(kpi):
    html = ['<h3 style="font-size:14px;font-weight:600;color:#37474f;margin-bottom:10px;border-left:4px solid #42a5f5;padding-left:10px">Cross-GEO KPI Comparison</h3>',
            '<div class="legend"><span style="background:#2e7d32">Good</span><span style="background:#f57f17">Moderate</span><span style="background:#c62828">Needs attention</span></div>',
            '<table><tr><th>GEO</th><th class="num">Contracts</th><th class="num">Coverage</th><th class="num">Attach</th><th class="num">Acceptance</th><th class="num">Change</th><th class="num">Att.Fail</th></tr>']
    geo = kpi['geo']
    for g in GEO_ORDER:
        d = geo.get(g, {})
        if not d: continue
        html.append(f'<tr><td><strong>{g}</strong></td><td class="num">{fmt(d["total"])}</td>'
                    f'<td class="num" {c_cov(d["coverage"])}>{d["coverage"]}%</td>'
                    f'<td class="num">{d["attach"]}%</td>'
                    f'<td class="num" {c_acc(d["acceptance"])}>{d["acceptance"]}%</td>'
                    f'<td class="num">{d["change"]}%</td>'
                    f'<td class="num" {c_af(d["attach_failure"])}>{d["attach_failure"]}%</td></tr>')
    html.append('</table>')
    return '\n'.join(html)

def gen_report(q, kpi, tt, prev_kpi=None):
    QMETA = {
        'Q1': {'fy': 'FY26/27', 'range': 'Apr 1 – Jun 30, 2026', 'period': '2026-04-01 to 2026-06-30'},
        'Q2': {'fy': 'FY26/27', 'range': 'Jul 1 – Sep 30, 2026', 'period': '2026-07-01 to 2026-09-30'},
        'Q4': {'fy': 'FY25/26', 'range': 'Jan 1 – Mar 31, 2026', 'period': '2026-01-01 to 2026-03-31'},
    }
    meta = QMETA[q]
    qlabel = f"{q} {meta['fy']} ({meta['range']})"
    qshort = q
    title = f"SSR Operational KPI Report — {q} {meta['fy']}"
    period = meta['period']

    ov = kpi['overall']
    geo = kpi['geo']

    nav_links = ''.join(f'<a href="#{g}">{g}</a>' for g in GEO_ORDER)
    nav = (f'<nav class="navbar"><span class="brand">{title}</span>'
           f'<a href="#summary">Executive Summary</a>{nav_links}'
           f'<a href="#term-type-cross">Product Analysis</a>'
           f'<span style="margin-left:auto;font-size:11px;color:#90caf9">Data: {period} | Contract-level</span></nav>')

    parts = ['<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">',
             f'<meta name="viewport" content="width=device-width,initial-scale=1.0">',
             f'<title>{title}</title>', CSS, '</head><body>', nav, '<div class="page">']

    # Executive summary
    parts.append(f'<div class="section" id="summary"><div class="sec-hdr"><h2>Executive Summary — {qlabel}</h2></div><div class="sec-body">')
    parts.append(f'<p class="insight">{fmt(ov["total"])} contracts across 4 GEOs (contract-level data). '
                 f'Overall acceptance {ov["acceptance"]}%, coverage {ov["coverage"]}%, attach {ov["attach"]}%. '
                 f'New CTO acceptance {kpi["origin"]["New CTO"]["acceptance"]}% vs Copied CTO {kpi["origin"]["Copied CTO"]["acceptance"]}% — the origin mix is the key driver of headline acceptance.</p>')
    parts.append('<div class="kpi-grid">')
    parts.append(exec_summary(kpi, prev_kpi))
    parts.append('</div>')
    parts.append(cross_geo_table(kpi))
    parts.append('</div></div>')

    # GEO sections
    for g in GEO_ORDER:
        d = geo.get(g, {})
        if not d: continue
        prev_g = prev_kpi['geo'].get(g) if prev_kpi else None
        parts.append(f'<div class="section" id="{g}"><div class="sec-hdr"><h2>{g} — Operational KPI Detail ({qshort} {meta["fy"]})</h2></div><div class="sec-body">')
        parts.append(kpi_dashboard(g, d, prev_g))
        parts.append(origin_section(g, kpi['geo_origin'].get(g, {})))
        parts.append(source_section(g, kpi['geo_source'].get(g, {})))
        parts.append(country_section(g, kpi['country'].get(g, {})))
        parts.append(monthly_section(g, kpi['geo_month'].get(g, {})))
        parts.append(term_type_section(g, tt))
        parts.append('</div></div>')

    # Cross-GEO product
    parts.append(cross_geo_product(tt))
    parts.append('</div></body></html>')
    return '\n'.join(parts)

def main():
    q1 = json.load(open(DATA / 'phase1_q1.json'))
    q2 = json.load(open(DATA / 'phase1_q2.json'))
    tt1 = json.load(open(DATA / 'term_type_q1.json'))
    tt2 = json.load(open(DATA / 'term_type_q2.json'))

    OUT.mkdir(exist_ok=True)
    r1 = gen_report('Q1', q1, tt1)
    (OUT / 'phase1_operational_kpi_report_q1.html').write_text(r1, encoding='utf-8')
    print(f"Written: {OUT / 'phase1_operational_kpi_report_q1.html'} ({len(r1):,} bytes)")

    r2 = gen_report('Q2', q2, tt2, prev_kpi=q1)
    (OUT / 'phase1_operational_kpi_report_q2.html').write_text(r2, encoding='utf-8')
    print(f"Written: {OUT / 'phase1_operational_kpi_report_q2.html'} ({len(r2):,} bytes)")

    # Q4 FY25/26 (optional — only if data present)
    q4p = DATA / 'phase1_q4.json'
    tt4p = DATA / 'term_type_q4.json'
    if q4p.exists() and tt4p.exists():
        q4 = json.load(open(q4p))
        tt4 = json.load(open(tt4p))
        r4 = gen_report('Q4', q4, tt4)
        (OUT / 'phase1_operational_kpi_report_q4.html').write_text(r4, encoding='utf-8')
        print(f"Written: {OUT / 'phase1_operational_kpi_report_q4.html'} ({len(r4):,} bytes)")

if __name__ == '__main__':
    main()
