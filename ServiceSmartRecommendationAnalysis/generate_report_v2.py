#!/usr/bin/env python3
"""
SSR Phase 1 — Operational KPI Report generator (V2 format).

Produces rich V2-format reports matching the layout of
`phase1_operational_kpi_report_v2.html` for three fiscal quarters:

  - FY25 Q4  (FY25/26 Q4, Jan 1 – Mar 31, 2026)   <- phase1_q4.json
  - FY26 Q1  (FY26/27 Q1, Apr 1 – Jun 30, 2026)   <- phase1_q1.json
  - FY26 Q2  (FY26/27 Q2, Jul 1 – Sep 30, 2026)   <- phase1_q2.json

Naming convention (per user): FY25/26 -> FY25, FY26/27 -> FY26.

Reads data/phase1_*.json + data/term_type_*.json, emits one self-contained
HTML per quarter into validation_output/.
"""
import json
from datetime import date
from pathlib import Path

DATA = Path(__file__).resolve().parent / "data"
OUT = Path(__file__).resolve().parent / "validation_output"

EM = '\u2014'  # em dash placeholder

GEO_ORDER = ['EMEA', 'AP', 'LA', 'NA']
TERM_ORDER = ['1Y', '2Y', '3Y', '4Y', '5Y']
TYPE_ORDER = ['Premier Support', 'Premier Support Plus', 'Onsite',
              'Depot / Mail-in', 'Other / Add-on']

QMETA = {
    'Q4': {'fy': 'FY25', 'range': 'Jan 1 \u2013 Mar 31, 2026', 'period': '2026-01-01 to 2026-03-31'},
    'Q1': {'fy': 'FY26', 'range': 'Apr 1 \u2013 Jun 30, 2026', 'period': '2026-04-01 to 2026-06-30'},
    'Q2': {'fy': 'FY26', 'range': 'Jul 1 \u2013 Sep 30, 2026', 'period': '2026-07-01 to 2026-09-30'},
}
# previous quarter for delta columns (None -> no comparison available)
PREV = {'Q4': None, 'Q1': 'Q4', 'Q2': 'Q1'}

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
.good-box{background:#e8f5e9;border-left:4px solid #2e7d32;padding:9px 13px;border-radius:4px;font-size:13px;color:#1b5e20;margin-bottom:10px;line-height:1.5}
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
.kpi-card .sub{font-size:11px;color:#888;line-height:1.4}
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

# ---- color helpers (thresholds aligned with the V2 template) ----
GREEN = '#2e7d32'; ORANGE = '#f57f17'; RED = '#c62828'

def c_acc(v):
    if v is None: return ''
    if v >= 55: return f'style="background:{GREEN};color:#fff"'
    if v >= 50: return f'style="background:{ORANGE};color:#fff"'
    return f'style="background:{RED};color:#fff"'

def c_cov(v):
    if v is None: return ''
    if v >= 97: return f'style="background:{GREEN};color:#fff"'
    if v >= 93: return f'style="background:{ORANGE};color:#fff"'
    return f'style="background:{RED};color:#fff"'

def c_af(v):
    if v is None: return ''
    if v <= 15: return f'style="background:{GREEN};color:#fff"'
    if v <= 25: return f'style="background:{ORANGE};color:#fff"'
    return f'style="background:{RED};color:#fff"'

def c_chg(v):
    if v is None: return ''
    if v >= 30: return f'style="background:{RED};color:#fff"'
    if v >= 25: return f'style="background:{ORANGE};color:#fff"'
    return f'style="background:{GREEN};color:#fff"'

def fmt(n): return f"{n:,}"

def pct(v, sign=False):
    if v is None: return '\u2014'
    if sign and v > 0: return f"+{v:.1f}"
    return f"{v:.1f}"

def delta_cell(cur, prev):
    if prev is None: return '<td class="num">\u2014</td>'
    d = round(cur - prev, 1)
    if abs(d) < 0.05: cls = 'trend-flat'
    elif d > 0: cls = 'trend-up'
    else: cls = 'trend-down'
    return f'<td class="num {cls}">{pct(d, sign=True)}pp</td>'

def acc_color(v):
    if v is None: return ''
    if v >= 55: return f'color:{GREEN}'
    if v >= 50: return f'color:{ORANGE}'
    return f'color:{RED}'


# ---- section builders ----
def kpi_grid(kpi):
    cards = []
    for g in GEO_ORDER:
        d = kpi['geo'].get(g)
        if not d: continue
        acc = d['acceptance']
        cards.append(
            f'<div class="kpi-card"><div class="geo-tag">{g}</div>'
            f'<div class="label">Acceptance Rate</div>'
            f'<div class="big" style="{acc_color(acc)}">{acc}%</div>'
            f'<div class="sub">{fmt(d["total"])} configs | {d["coverage"]}% coverage</div>'
            f'<div class="sub">Attach: {d["attach"]}% | Change: {d["change"]}% | Att.Fail: {d["attach_failure"]}%</div></div>')
    return '\n'.join(cards)


def cross_geo_table(kpi):
    html = ['<table><tr><th>GEO</th><th class="num">Configs</th><th class="num">Coverage</th>'
            '<th class="num">AI Cov</th><th class="num">Attach</th><th class="num">Acceptance</th>'
            '<th class="num">Change</th><th class="num">Influence</th><th class="num">Att.Fail</th></tr>']
    for g in GEO_ORDER:
        d = kpi['geo'].get(g)
        if not d: continue
        html.append(
            f'<tr><td><strong>{g}</strong></td>'
            f'<td class="num">{fmt(d["total"])}</td>'
            f'<td class="num" {c_cov(d["coverage"])}>{d["coverage"]}%</td>'
            f'<td class="num">{d["ai_coverage"]}%</td>'
            f'<td class="num">{d["attach"]}%</td>'
            f'<td class="num" {c_acc(d["acceptance"])}>{d["acceptance"]}%</td>'
            f'<td class="num" {c_chg(d["change"])}>{d["change"]}%</td>'
            f'<td class="num">{d["influence"]}%</td>'
            f'<td class="num" {c_af(d["attach_failure"])}>{d["attach_failure"]}%</td></tr>')
    ov = kpi['overall']
    html.append(
        f'<tr style="font-weight:700;background:#f0f2f5"><td><strong>Global (All 4 GEOs)</strong></td>'
        f'<td class="num">{fmt(ov["total"])}</td>'
        f'<td class="num" {c_cov(ov["coverage"])}>{ov["coverage"]}%</td>'
        f'<td class="num">{ov["ai_coverage"]}%</td>'
        f'<td class="num">{ov["attach"]}%</td>'
        f'<td class="num" {c_acc(ov["acceptance"])}>{ov["acceptance"]}%</td>'
        f'<td class="num" {c_chg(ov["change"])}>{ov["change"]}%</td>'
        f'<td class="num">{ov["influence"]}%</td>'
        f'<td class="num" {c_af(ov["attach_failure"])}>{ov["attach_failure"]}%</td></tr>')
    html.append('</table>')
    return '\n'.join(html)


def new_cto_trend_table(kpi, prev):
    html = ['<table><tr><th>GEO</th><th class="num">New CTO Acc (Prev)</th>'
            '<th class="num">New CTO Acc (Current)</th><th class="num">\u0394</th>'
            '<th class="num">New CTO Share</th><th>Assessment</th></tr>']
    for g in GEO_ORDER:
        go = kpi['geo_origin'].get(g, {})
        nc = go.get('New CTO', {})
        if not nc: continue
        cur = nc['acceptance']
        share = round(nc['total'] / kpi['geo'][g]['total'] * 100, 1) if kpi['geo'][g]['total'] else 0
        if prev and prev['geo_origin'].get(g, {}).get('New CTO', {}):
            pv = prev['geo_origin'][g]['New CTO']['acceptance']
            d = round(cur - pv, 1)
            pv_s = f'{pv}%'
            if d >= 3: assess = 'Improving'
            elif d <= -2: assess = '\u26a0 Genuine decline'
            else: assess = 'Flat / marginal'
            d_s = f'<td class="num" style="color:{"#2e7d32" if d>=0 else "#c62828"};font-weight:700">{pct(d, sign=True)}pp</td>'
        else:
            pv_s = '\u2014'; d_s = '<td class="num">\u2014</td>'; assess = 'Baseline'
        html.append(
            f'<tr><td><strong>{g}</strong></td><td class="num">{pv_s}</td>'
            f'<td class="num" {c_acc(cur)}>{cur}%</td>{d_s}'
            f'<td class="num">{share}%</td><td>{assess}</td></tr>')
    html.append('</table>')
    return '\n'.join(html)


def kpi_dashboard(g, d, prev_g):
    rows = []
    def row(name, cnt, rate, prev_rate, style='', is_total=False):
        cnt_s = f'<td class="num">{fmt(cnt) if cnt is not None else EM}</td>'
        rate_s = f'<td class="num" {style}>{pct(rate)}%</td>' if rate is not None else '<td class="num">\u2014</td>'
        if prev_g is None:
            return f'<tr><td>{name}</td>{cnt_s}{rate_s}<td class="num">\u2014</td><td class="num">\u2014</td></tr>'
        if is_total:
            pv = f'<td class="num">{fmt(int(prev_rate)) if prev_rate is not None else EM}</td>'
            return f'<tr><td>{name}</td>{cnt_s}{rate_s}{pv}<td class="num">\u2014</td></tr>'
        pv = f'<td class="num">{pct(prev_rate)}%</td>' if prev_rate is not None else '<td class="num">\u2014</td>'
        dlt = delta_cell(rate, prev_rate) if (rate is not None and prev_rate is not None) else '<td class="num">\u2014</td>'
        return f'<tr><td>{name}</td>{cnt_s}{rate_s}{pv}{dlt}</tr>'

    hdr = '<tr><th>Metric</th><th class="num">Count</th><th class="num">Rate</th>'
    if prev_g:
        hdr += '<th class="num">Prev Rate</th><th class="num">\u0394</th>'
    else:
        hdr += '<th class="num">Prev</th><th class="num">\u0394</th>'
    hdr += '</tr>'

    rows.append(row('Total Configs', d['total'], None, prev_g['total'] if prev_g else None, is_total=True))
    rows.append(row('Default Coverage', d['has_default'], d['coverage'], prev_g['coverage'] if prev_g else None, c_cov(d['coverage'])))
    rows.append(row('AI Coverage', round(d['ai_coverage'] * d['total'] / 100), d['ai_coverage'], prev_g['ai_coverage'] if prev_g else None))
    rows.append(row('Service Attach Rate', d['has_selected'], d['attach'], prev_g['attach'] if prev_g else None))
    rows.append(row('Acceptance Rate', d['accepted'], d['acceptance'], prev_g['acceptance'] if prev_g else None, c_acc(d['acceptance'])))
    rows.append(row('Change Rate', d['changed'], d['change'], prev_g['change'] if prev_g else None, c_chg(d['change'])))
    rows.append(row('Influence Rate', d['accepted'] + d['changed'], d['influence'], prev_g['influence'] if prev_g else None))
    rows.append(row('Attachment Failure', d['has_default'] - d['has_selected'], d['attach_failure'], prev_g['attach_failure'] if prev_g else None, c_af(d['attach_failure'])))
    rows.append(row('No Default', d['total'] - d['has_default'], d['no_default'], prev_g['no_default'] if prev_g else None))
    return (f'<div class="sub"><h3>A. KPI Dashboard (n={fmt(d["total"])})</h3>'
            '<div class="legend"><span style="background:#2e7d32">Good</span>'
            '<span style="background:#f57f17">Moderate</span><span style="background:#c62828">Needs attention</span></div>'
            '<table>' + hdr + '\n'.join(rows) + '</table></div>')


def origin_section(g, go):
    html = ['<div class="sub"><h3>B. KPI by Config Origin</h3>',
            '<table><tr><th>Origin</th><th class="num">Configs</th><th class="num">Coverage</th>'
            '<th class="num">Attach</th><th class="num">Acceptance</th><th class="num">Change</th><th class="num">Att.Fail</th></tr>']
    tags = {'New CTO': 'tag-new', 'Copied CTO': 'tag-copied', 'MTM': 'tag-mtm'}
    for o in ['New CTO', 'Copied CTO', 'MTM']:
        d = go.get(o)
        if not d: continue
        html.append(f'<tr><td><span class="tag {tags[o]}">{o}</span></td>'
                    f'<td class="num">{fmt(d["total"])}</td>'
                    f'<td class="num" {c_cov(d["coverage"])}>{d["coverage"]}%</td>'
                    f'<td class="num">{d["attach"]}%</td>'
                    f'<td class="num" {c_acc(d["acceptance"])}>{d["acceptance"]}%</td>'
                    f'<td class="num" {c_chg(d["change"])}>{d["change"]}%</td>'
                    f'<td class="num" {c_af(d["attach_failure"])}>{d["attach_failure"]}%</td></tr>')
    html.append('</table></div>')
    return '\n'.join(html)


def source_section(g, gs):
    html = ['<div class="sub"><h3>C. AI vs Non-AI Default Acceptance</h3>',
            '<table><tr><th>Default Source</th><th class="num">Configs</th><th class="num">Coverage</th>'
            '<th class="num">Attach</th><th class="num">Acceptance</th><th class="num">Change</th><th class="num">Att.Fail</th></tr>']
    for s in ['AI', 'Non-AI', 'ALL']:
        d = gs.get(s)
        if not d: continue
        html.append(f'<tr><td><strong>{s}</strong></td>'
                    f'<td class="num">{fmt(d["total"])}</td>'
                    f'<td class="num" {c_cov(d["coverage"])}>{d["coverage"]}%</td>'
                    f'<td class="num">{d["attach"]}%</td>'
                    f'<td class="num" {c_acc(d["acceptance"])}>{d["acceptance"]}%</td>'
                    f'<td class="num" {c_chg(d["change"])}>{d["change"]}%</td>'
                    f'<td class="num" {c_af(d["attach_failure"])}>{d["attach_failure"]}%</td></tr>')
    html.append('</table></div>')
    return '\n'.join(html)


def country_section(g, cs, top=15):
    items = list(cs.items())[:top]
    html = [f'<div class="sub"><h3>D. Country Drill-Down (Top {len(items)})</h3>',
            '<table><tr><th>Country</th><th class="num">Configs</th><th class="num">Coverage</th>'
            '<th class="num">Acceptance</th><th class="num">Change</th><th class="num">Att.Fail</th><th class="num">AI Cov</th></tr>']
    for c, d in items:
        html.append(f'<tr><td><strong>{c}</strong></td>'
                    f'<td class="num">{fmt(d["total"])}</td>'
                    f'<td class="num" {c_cov(d["coverage"])}>{d["coverage"]}%</td>'
                    f'<td class="num" {c_acc(d["acceptance"])}>{d["acceptance"]}%</td>'
                    f'<td class="num" {c_chg(d["change"])}>{d["change"]}%</td>'
                    f'<td class="num" {c_af(d["attach_failure"])}>{d["attach_failure"]}%</td>'
                    f'<td class="num">{d["ai_coverage"]}%</td></tr>')
    html.append('</table></div>')
    return '\n'.join(html)


def monthly_section(gm, title='E. Monthly Trend'):
    html = [f'<div class="sub"><h3>{title}</h3>',
            '<table><tr><th>Month</th><th class="num">Configs</th><th class="num">Coverage</th>'
            '<th class="num">Attach</th><th class="num">Acceptance</th><th class="num">Change</th>'
            '<th class="num">AI Cov</th><th class="num">Att.Fail</th></tr>']
    for m in sorted(gm.keys()):
        d = gm[m]
        html.append(f'<tr><td><strong>{m}</strong></td>'
                    f'<td class="num">{fmt(d["total"])}</td>'
                    f'<td class="num" {c_cov(d["coverage"])}>{d["coverage"]}%</td>'
                    f'<td class="num">{d["attach"]}%</td>'
                    f'<td class="num" {c_acc(d["acceptance"])}>{d["acceptance"]}%</td>'
                    f'<td class="num" {c_chg(d["change"])}>{d["change"]}%</td>'
                    f'<td class="num">{d["ai_coverage"]}%</td>'
                    f'<td class="num" {c_af(d["attach_failure"])}>{d["attach_failure"]}%</td></tr>')
    html.append('</table></div>')
    return '\n'.join(html)


def term_type_section(tt_geo, title='F. Service Product Analysis \u2014 Term \u00d7 Type'):
    term_agg = {}
    type_agg = {}
    combos = []
    for term, types in tt_geo.items():
        if term not in TERM_ORDER: continue
        for typ, c in types.items():
            if typ not in TYPE_ORDER: continue
            t = term_agg.setdefault(term, {'total': 0, 'acc_s': 0, 'chg_s': 0, 'af_s': 0})
            t['total'] += c['total']; t['acc_s'] += c['total'] * c['acceptance']
            t['chg_s'] += c['total'] * c['change']; t['af_s'] += c['total'] * c['att_fail']
            ty = type_agg.setdefault(typ, {'total': 0, 'acc_s': 0, 'chg_s': 0, 'af_s': 0})
            ty['total'] += c['total']; ty['acc_s'] += c['total'] * c['acceptance']
            ty['chg_s'] += c['total'] * c['change']; ty['af_s'] += c['total'] * c['att_fail']
            combos.append((term, typ, c['total'], c['acceptance'], c['change']))

    n_parsed = sum(v['total'] for v in term_agg.values())

    html = [f'<div class="sub"><h3>{title}</h3>',
            f'<p class="insight">{fmt(n_parsed)} configs with parsable term (1Y\u20135Y) and type.</p>']
    html.append('<h4>By Term</h4><table><tr><th>Term</th><th class="num">Configs</th>'
                '<th class="num">Acceptance</th><th class="num">Change</th><th class="num">Att.Fail</th></tr>')
    for term in TERM_ORDER:
        d = term_agg.get(term)
        if not d or d['total'] == 0: continue
        acc = round(d['acc_s'] / d['total'], 1); chg = round(d['chg_s'] / d['total'], 1)
        af = round(d['af_s'] / d['total'], 1)
        html.append(f'<tr><td><strong>{term}</strong></td><td class="num">{fmt(d["total"])}</td>'
                    f'<td class="num" {c_acc(acc)}>{acc}%</td><td class="num" {c_chg(chg)}>{chg}%</td>'
                    f'<td class="num" {c_af(af)}>{af}%</td></tr>')
    html.append('</table>')

    html.append('<h4>By Type</h4><table><tr><th>Type</th><th class="num">Configs</th>'
                '<th class="num">Acceptance</th><th class="num">Change</th><th class="num">Att.Fail</th></tr>')
    for typ in TYPE_ORDER:
        t = type_agg.get(typ)
        if not t or t['total'] == 0: continue
        acc = round(t['acc_s'] / t['total'], 1); chg = round(t['chg_s'] / t['total'], 1)
        af = round(t['af_s'] / t['total'], 1)
        html.append(f'<tr><td><strong>{typ}</strong></td><td class="num">{fmt(t["total"])}</td>'
                    f'<td class="num" {c_acc(acc)}>{acc}%</td><td class="num" {c_chg(chg)}>{chg}%</td>'
                    f'<td class="num" {c_af(af)}>{af}%</td></tr>')
    html.append('</table>')

    html.append('<h4>Top Combinations</h4><table><tr><th>Combination</th><th class="num">Configs</th>'
                '<th class="num">Acceptance</th><th class="num">Change</th></tr>')
    for term, typ, total, acc, chg in sorted(combos, key=lambda x: -x[2])[:8]:
        html.append(f'<tr><td><strong>{term} {typ}</strong></td><td class="num">{fmt(total)}</td>'
                    f'<td class="num" {c_acc(acc)}>{acc}%</td><td class="num" {c_chg(chg)}>{chg}%</td></tr>')
    html.append('</table></div>')
    return '\n'.join(html)


def merge_term_type_global(tt):
    """Merge per-GEO term_type into a single global {term: {type: {...}}} structure."""
    merged = {}
    for g in GEO_ORDER:
        geo_tt = tt.get(g, {})
        for term, types in geo_tt.items():
            for typ, c in types.items():
                m = merged.setdefault(term, {}).setdefault(typ, {'total': 0, 'acc_w': 0.0, 'chg_w': 0.0, 'af_w': 0.0})
                m['total'] += c['total']
                m['acc_w'] += c['total'] * c['acceptance']
                m['chg_w'] += c['total'] * c['change']
                m['af_w'] += c['total'] * c['att_fail']
    out = {}
    for term, types in merged.items():
        for typ, m in types.items():
            t = m['total']
            out.setdefault(term, {})[typ] = {
                'total': t,
                'acceptance': round(m['acc_w'] / t, 1) if t else 0,
                'change': round(m['chg_w'] / t, 1) if t else 0,
                'att_fail': round(m['af_w'] / t, 1) if t else 0,
            }
    return out


def global_analysis_section(kpi, tt):
    """Global (all-4-GEO) Monthly Trend + Service Product Analysis for the exec summary."""
    gtt = merge_term_type_global(tt)
    return '\n'.join([
        monthly_section(kpi['month'], title='Global Monthly Trend (All 4 GEOs)'),
        term_type_section(gtt, title='Global Service Product Analysis \u2014 Term \u00d7 Type'),
    ])


def cross_geo_product(tt, kpi):
    html = ['<div class="section" id="term-type-cross"><div class="sec-hdr">'
            '<h2>Cross-GEO \u2014 Service Product Analysis Comparison</h2></div><div class="sec-body">']

    def comb_acc(g, term, typ):
        cell = tt.get(g, {}).get(term, {}).get(typ)
        if not cell: return None
        return cell['total'], cell['acceptance'], cell['change']

    for title, term, typ, color in [
        ('3Y Premier Support \u2014 Largest Volume Product (All GEOs)', '3Y', 'Premier Support', '#c62828'),
        ('Premier Support Plus (All Terms) \u2014 Premium Product Trust Gap', None, 'Premier Support Plus', '#f57c00'),
    ]:
        html.append(f'<h3 style="font-size:14px;font-weight:600;color:#37474f;margin-bottom:10px;'
                    f'border-left:4px solid {color};padding-left:10px">{title}</h3>')
        html.append('<table><tr><th>GEO</th><th class="num">Configs</th><th class="num">Acceptance</th>'
                    '<th class="num">Change</th><th>Assessment</th></tr>')
        for g in GEO_ORDER:
            if term:
                c = comb_acc(g, term, typ)
            else:
                # aggregate across terms
                tot = acc_s = chg_s = 0
                for t2 in TERM_ORDER:
                    cell = tt.get(g, {}).get(t2, {}).get(typ)
                    if cell:
                        tot += cell['total']; acc_s += cell['total'] * cell['acceptance']
                        chg_s += cell['total'] * cell['change']
                c = (tot, round(acc_s / tot, 1), round(chg_s / tot, 1)) if tot else None
            if not c or c[0] == 0: continue
            tot, acc, chg = c
            if acc >= 55: assess = 'Strong'
            elif acc >= 45: assess = 'Middle'
            else: assess = '\u26a0 Weak'
            html.append(f'<tr><td><strong>{g}</strong></td><td class="num">{fmt(tot)}</td>'
                        f'<td class="num" {c_acc(acc)}>{acc}%</td><td class="num" {c_chg(chg)}>{chg}%</td>'
                        f'<td>{assess}</td></tr>')
        html.append('</table>')
    html.append('</div></div>')
    return '\n'.join(html)


# ---- narrative ----
def exec_narrative(kpi, prev, meta):
    ov = kpi['overall']
    parts = []
    parts.append(f'<p class="insight">{fmt(ov["total"])} configurations across 4 GEOs. '
                 f'Overall acceptance {ov["acceptance"]}%, coverage {ov["coverage"]}%, '
                 f'attach {ov["attach"]}%, AI coverage {ov["ai_coverage"]}%. '
                 f'New CTO acceptance {kpi["origin"]["New CTO"]["acceptance"]}% vs '
                 f'Copied CTO {kpi["origin"]["Copied CTO"]["acceptance"]}% \u2014 the origin mix '
                 f'is the key driver of headline acceptance.</p>')
    return '\n'.join(parts)


def findings_narrative(kpi, prev):
    """Generate QoQ critical-finding + concern narrative. Returns a list of HTML strings."""
    if not prev:
        return []
    ov_cur = kpi['overall']['acceptance']
    ov_d = round(ov_cur - prev['overall']['acceptance'], 1)
    improving, declining = [], []
    for g in GEO_ORDER:
        cur = kpi['geo_origin'].get(g, {}).get('New CTO', {})
        pv = prev['geo_origin'].get(g, {}).get('New CTO', {})
        if not (cur and pv):
            continue
        d = round(cur['acceptance'] - pv['acceptance'], 1)
        if d >= 3:
            improving.append((g, pv['acceptance'], cur['acceptance'], d))
        elif d <= -2:
            declining.append((g, pv['acceptance'], cur['acceptance'], d))

    out = []
    # Critical finding: New CTO acceptance trend
    if improving or declining:
        seg = []
        if improving:
            seg.append('New CTO acceptance <strong>improved</strong> in '
                       + ', '.join(f'{g} ({pv}% \u2192 {cur}%, {pct(d, sign=True)}pp)'
                                   for g, pv, cur, d in improving))
        if declining:
            seg.append('New CTO acceptance <strong>declined</strong> in '
                       + ', '.join(f'{g} ({pv}% \u2192 {cur}%, {pct(d, sign=True)}pp)'
                                   for g, pv, cur, d in declining))
        body = '; '.join(seg) + '.'
        out.append(
            '<div style="margin-top:20px">'
            '<h3 style="font-size:14px;font-weight:600;color:#37474f;margin-bottom:10px;'
            'border-left:4px solid #c62828;padding-left:10px">\u26a0 Critical Finding: New CTO Acceptance Trend</h3>'
            f'<p class="critical">Headline acceptance moved {pct(ov_d, sign=True)}pp to {ov_cur}%. '
            f'Beneath the headline, {body}</p>')
        out.append(new_cto_trend_table(kpi, prev))
        out.append('</div>')

    # Concern: GEOs with genuine overall acceptance decline
    decl_geo = []
    for g in GEO_ORDER:
        cur = kpi['geo'].get(g, {}).get('acceptance')
        pv = prev['geo'].get(g, {}).get('acceptance')
        if cur is None or pv is None:
            continue
        d = round(cur - pv, 1)
        if d <= -2:
            decl_geo.append((g, pv, cur, d))
    if decl_geo:
        items = '; '.join(f'{g}: {pv}% \u2192 {cur}% ({pct(d, sign=True)}pp)'
                          for g, pv, cur, d in decl_geo)
        out.append(
            '<div style="margin-top:16px">'
            '<h3 style="font-size:14px;font-weight:600;color:#37474f;margin-bottom:10px;'
            'border-left:4px solid #f57c00;padding-left:10px">\u26a0 Overall Acceptance Declining \u2014 Genuine Concern</h3>'
            f'<p class="warn">{items}. These GEOs need investigation \u2014 cross-check New CTO trend in the table above.</p></div>')
    return out


def gen_report(q, kpi, tt, prev_kpi=None):
    meta = QMETA[q]
    fy = meta['fy']; qlabel = f'{q} {fy} ({meta["range"]})'
    title = f'SSR Operational KPI Report \u2014 {q} {fy}'

    nav = (f'<nav class="navbar"><span class="brand">{title}</span>'
           f'<a href="#summary">Executive Summary</a>'
           + ''.join(f'<a href="#{g}">{g}</a>' for g in GEO_ORDER)
           + f'<a href="#term-type-cross">Product Analysis</a>'
           f'<span style="margin-left:auto;font-size:11px;color:#90caf9">Data: {meta["period"]} | Generated: {date.today().isoformat()}</span></nav>')

    parts = ['<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">',
             '<meta name="viewport" content="width=device-width,initial-scale=1.0">',
             f'<title>{title}</title>', CSS, '</head><body>', nav, '<div class="page">']

    # Executive summary
    parts.append(f'<div class="section" id="summary"><div class="sec-hdr">'
                 f'<h2>Executive Summary \u2014 {qlabel}</h2></div><div class="sec-body">')
    parts.append(exec_narrative(kpi, prev_kpi, meta))
    parts.append('<div class="kpi-grid">')
    parts.append(kpi_grid(kpi))
    parts.append('</div>')
    parts.append(f'<h3 style="font-size:14px;font-weight:600;color:#37474f;margin-bottom:10px;'
                 f'border-left:4px solid #42a5f5;padding-left:10px">Cross-GEO KPI Comparison \u2014 {qlabel}</h3>')
    parts.append('<div class="legend"><span style="background:#2e7d32">Good</span>'
                 '<span style="background:#f57f17">Moderate</span><span style="background:#c62828">Needs attention</span></div>')
    parts.append(cross_geo_table(kpi))
    for f in findings_narrative(kpi, prev_kpi):
        parts.append(f)
    parts.append(global_analysis_section(kpi, tt))
    parts.append('</div></div>')

    # GEO sections
    for g in GEO_ORDER:
        d = kpi['geo'].get(g)
        if not d: continue
        prev_g = prev_kpi['geo'].get(g) if prev_kpi else None
        parts.append(f'<div class="section" id="{g}"><div class="sec-hdr">'
                     f'<h2>{g} \u2014 Operational KPI Detail ({q} {fy})</h2></div><div class="sec-body">')
        parts.append(kpi_dashboard(g, d, prev_g))
        parts.append(origin_section(g, kpi['geo_origin'].get(g, {})))
        parts.append(source_section(g, kpi['geo_source'].get(g, {})))
        parts.append(country_section(g, kpi['country'].get(g, {})))
        parts.append(monthly_section(kpi['geo_month'].get(g, {})))
        parts.append(term_type_section(tt.get(g, {})))
        parts.append('</div></div>')

    # Cross-GEO product
    parts.append(cross_geo_product(tt, kpi))
    parts.append('</div></body></html>')
    return '\n'.join(parts)


def main():
    OUT.mkdir(exist_ok=True)
    loaded = {}
    for q in ['Q4', 'Q1', 'Q2']:
        kpi = json.load(open(DATA / f'phase1_{q.lower()}.json'))
        tt = json.load(open(DATA / f'term_type_{q.lower()}.json'))
        loaded[q] = (kpi, tt)
    for q in ['Q4', 'Q1', 'Q2']:
        kpi, tt = loaded[q]
        prev = loaded[PREV[q]][0] if PREV[q] else None
        meta = QMETA[q]
        html = gen_report(q, kpi, tt, prev_kpi=prev)
        out = OUT / f'phase1_operational_kpi_report_v2_{meta["fy"].lower()}{q.lower()}.html'
        out.write_text(html, encoding='utf-8')
        print(f'Written: {out} ({len(html):,} bytes)')

if __name__ == '__main__':
    main()
