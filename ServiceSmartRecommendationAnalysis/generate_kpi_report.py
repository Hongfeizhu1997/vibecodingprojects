#!/usr/bin/env python3
"""
Service Smart Recommendation — Operational KPI Report
Generates: validation_output/operational_kpi_report.html

Sections per GEO:
  A. KPI Dashboard
  B. Country Drill-Down
  C. Recommendation Profile (AI rows)
  D. Coverage Gaps (Improvement Area 1)
  E. Low Acceptance Segments (Improvement Area 2)
  F. Attachment Failure Analysis (Improvement Area 3)
  G. Monthly Trend (Improvement Area 4)
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime

# ── CONFIG ─────────────────────────────────────────────────────────────────────
CSV_FILE = '20260329120322330.csv'
OUT_DIR  = 'validation_output'
OUT_FILE = os.path.join(OUT_DIR, 'operational_kpi_report.html')

GEOS = ['EMEA', 'AP', 'LA', 'NA']
GEO_FULL = {
    'EMEA': 'EMEA — Europe, Middle East &amp; Africa',
    'AP':   'AP — Asia-Pacific',
    'LA':   'LA — Latin America',
    'NA':   'NA — North America',
}
MIN_VOL_MT  = 50   # min defaults for machine-type analysis
MIN_VOL_CAT = 20   # min defaults for category analysis

# Analysis start dates: only include data from go-live onwards
# EMEA went live 2025-09-28 (pilot FR/ES/DK from 2025-08-15, full EMEA from 2025-09-28)
# AP, LA, NA went live 2025-11-28
GEO_START = {
    'EMEA': pd.Timestamp('2025-09-28'),
    'AP':   pd.Timestamp('2025-11-28'),
    'LA':   pd.Timestamp('2025-11-28'),
    'NA':   pd.Timestamp('2025-11-28'),
}

# ── COLOR THRESHOLDS ───────────────────────────────────────────────────────────
def color_for(metric, value):
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return '#f5f5f5'
    v = float(value)
    if metric == 'acceptance':
        return '#c8e6c9' if v >= 55 else ('#fff9c4' if v >= 45 else '#ffcdd2')
    if metric == 'change':
        return '#c8e6c9' if v <= 25 else ('#fff9c4' if v <= 35 else '#ffcdd2')
    if metric == 'coverage':
        return '#c8e6c9' if v >= 95 else ('#fff9c4' if v >= 90 else '#ffcdd2')
    if metric == 'attach':
        return '#c8e6c9' if v >= 75 else ('#fff9c4' if v >= 65 else '#ffcdd2')
    if metric == 'att_fail':
        return '#c8e6c9' if v <= 20 else ('#fff9c4' if v <= 30 else '#ffcdd2')
    if metric == 'no_default':
        return '#c8e6c9' if v <= 5 else ('#fff9c4' if v <= 10 else '#ffcdd2')
    return '#ffffff'


def fp(v, d=1):
    """Format percentage."""
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return '—'
    return f'{float(v):.{d}f}%'


def fc(v):
    """Format integer count with commas."""
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return '—'
    return f'{int(v):,}'


# ── DATA LOADING ───────────────────────────────────────────────────────────────
def load_data():
    print('Loading CSV...', flush=True)
    df = pd.read_csv(CSV_FILE, encoding='utf-8-sig', keep_default_na=False,
                     low_memory=False)
    df.columns = df.columns.str.strip()

    # Parse dates
    df['contract_creation_date'] = pd.to_datetime(
        df['contract_creation_date'], errors='coerce')
    df['year_month'] = (df['contract_creation_date']
                        .dt.to_period('M')
                        .astype('object')
                        .where(df['contract_creation_date'].notna(), other=None))

    # Normalise key string columns
    str_cols = ['default_pn', 'selection_pn', 'selectedfrom', 'defaultfrom',
                'category1', 'category2', 'machinetype', 'endcustomercountry',
                'geo', 'default_term', 'default_servicetype',
                'selection_term', 'selection_servicetype']
    for col in str_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
        else:
            df[col] = ''

    # Metric flags (consistent with validated definitions)
    df['has_default']  = df['default_pn'] != ''
    df['is_ai']        = df['defaultfrom'] == 'AI'
    df['has_sold']     = df['selection_pn'] != ''
    df['def_and_sold'] = df['has_default'] & df['has_sold']
    df['is_accepted']  = df['has_default'] & (df['selection_pn'] == df['default_pn'])
    df['is_changed']   = df['def_and_sold'] & ~df['is_accepted']
    df['no_default']   = ~df['has_default']
    df['att_failure']  = df['has_default'] & ~df['has_sold']

    d_min = df['contract_creation_date'].min()
    d_max = df['contract_creation_date'].max()
    print(f'  Loaded {len(df):,} rows', flush=True)
    print(f'  Date range : {d_min.date()} to {d_max.date()}', flush=True)
    print(f'  GEO counts : {df["geo"].value_counts().to_dict()}', flush=True)
    return df, d_min, d_max


# ── KPI COMPUTATION ────────────────────────────────────────────────────────────
def compute_kpis(sub):
    n        = len(sub)
    defaults = int(sub['has_default'].sum())
    def_sold = int(sub['def_and_sold'].sum())
    accepted = int(sub['is_accepted'].sum())
    changed  = int(sub['is_changed'].sum())
    ai_n     = int(sub['is_ai'].sum())
    att_fail = int(sub['att_failure'].sum())
    no_def   = int(sub['no_default'].sum())

    p = lambda a, b: a / b * 100 if b > 0 else float('nan')
    return {
        'total':          n,
        'ai_count':       ai_n,
        'ai_pct':         p(ai_n, n),
        'defaults':       defaults,
        'coverage_pct':   p(defaults, n),
        'def_sold':       def_sold,
        'attach_pct':     p(def_sold, n),
        'accepted':       accepted,
        'acceptance_pct': p(accepted, defaults),
        'changed':        changed,
        'change_pct':     p(changed, defaults),
        'influence_pct':  p(def_sold, defaults),
        'att_fail':       att_fail,
        'att_fail_pct':   p(att_fail, defaults),
        'no_default':     no_def,
        'no_default_pct': p(no_def, n),
    }


# ── HTML HELPERS ───────────────────────────────────────────────────────────────
STYLE = """
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',Arial,sans-serif;background:#f0f2f5;color:#222;font-size:14px}
.navbar{background:#1a237e;color:#fff;padding:12px 24px;display:flex;align-items:center;
        gap:20px;position:sticky;top:0;z-index:100;box-shadow:0 2px 8px rgba(0,0,0,.35)}
.navbar .brand{font-weight:700;font-size:15px;white-space:nowrap}
.navbar a{color:#bbdefb;text-decoration:none;padding:4px 10px;border-radius:4px;
          font-size:13px;white-space:nowrap}
.navbar a:hover{background:rgba(255,255,255,.15);color:#fff}
.navbar .meta{margin-left:auto;font-size:11px;color:#90caf9;white-space:nowrap}
.page{max-width:1280px;margin:0 auto;padding:20px 24px}
.section{background:#fff;border-radius:8px;box-shadow:0 1px 4px rgba(0,0,0,.1);
         margin-bottom:28px;overflow:hidden}
.section-header{background:#1a237e;color:#fff;padding:14px 20px}
.section-header h2{font-size:18px;font-weight:600}
.section-body{padding:20px}
.subsection{margin-bottom:28px}
.subsection:last-child{margin-bottom:0}
.subsection h3{font-size:14px;font-weight:600;color:#37474f;margin-bottom:10px;
               border-left:4px solid #42a5f5;padding-left:10px}
.subsection h4{font-size:13px;font-weight:600;color:#555;margin:16px 0 8px}
.insight{background:#e3f2fd;border-left:4px solid #1976d2;padding:9px 13px;
         border-radius:4px;font-size:13px;color:#0d47a1;margin-bottom:10px;line-height:1.5}
table{border-collapse:collapse;width:100%;font-size:13px}
th{background:#37474f;color:#fff;padding:7px 11px;text-align:left;font-weight:600;
   white-space:nowrap}
td{padding:6px 11px;border-bottom:1px solid #eee;vertical-align:middle}
tr:last-child td{border-bottom:none}
tr:hover td{filter:brightness(.97)}
.num{text-align:right;font-family:'Courier New',monospace;white-space:nowrap}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:4px}
.card-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:22px}
.kpi-card{background:#f5f7ff;border:1px solid #e8eaf6;border-radius:8px;padding:14px}
.kpi-card .geo-tag{display:inline-block;background:#1a237e;color:#fff;border-radius:4px;
                   padding:2px 9px;font-size:12px;font-weight:700;margin-bottom:6px}
.kpi-card .label{font-size:11px;color:#666;text-transform:uppercase;letter-spacing:.5px}
.kpi-card .big{font-size:26px;font-weight:700;margin:3px 0}
.kpi-card .sub{font-size:11px;color:#888}
.legend{display:flex;gap:12px;font-size:12px;margin-bottom:8px;align-items:center}
.legend span{padding:2px 8px;border-radius:10px}
code{background:#f5f5f5;border-radius:3px;padding:1px 5px;font-size:12px}
</style>
"""

LEGEND = """<div class="legend">
  <span style="background:#c8e6c9;color:#1b5e20">&#9679; Good</span>
  <span style="background:#fff9c4;color:#f57f17">&#9679; Moderate</span>
  <span style="background:#ffcdd2;color:#b71c1c">&#9679; Needs attention</span>
</div>"""


def pct_cell(v, metric):
    bg = color_for(metric, v)
    return f'<td class="num" style="background:{bg}">{fp(v)}</td>'


# ── SECTION BUILDERS ───────────────────────────────────────────────────────────

def build_kpi_table(k):
    rows = [
        ('Total Configurations', fc(k['total']), '—', None, None),
        ('Default Coverage (any default shown)', fc(k['defaults']),
         fp(k['coverage_pct']), 'coverage', k['coverage_pct']),
        ('AI Coverage (AI-sourced default)', fc(k['ai_count']),
         fp(k['ai_pct']), None, None),
        ('Service Attach Rate', fc(k['def_sold']),
         fp(k['attach_pct']), 'attach', k['attach_pct']),
        ('Acceptance Rate (rep kept AI default)', fc(k['accepted']),
         fp(k['acceptance_pct']), 'acceptance', k['acceptance_pct']),
        ('Change Rate (rep overrode default)', fc(k['changed']),
         fp(k['change_pct']), 'change', k['change_pct']),
        ('Influence Rate (accepted + changed) / defaults', fc(k['def_sold']),
         fp(k['influence_pct']), None, None),
        ('Attachment Failure (default shown, nothing sold)', fc(k['att_fail']),
         fp(k['att_fail_pct']), 'att_fail', k['att_fail_pct']),
        ('No Default (no recommendation available)', fc(k['no_default']),
         fp(k['no_default_pct']), 'no_default', k['no_default_pct']),
    ]
    h = '<table><tr><th>Metric</th><th style="text-align:right">Count</th><th style="text-align:right">Rate</th></tr>'
    for label, cnt, rate, mtype, mval in rows:
        bg = f'background:{color_for(mtype, mval)};' if mtype else ''
        h += f'<tr><td>{label}</td><td class="num">{cnt}</td><td class="num" style="{bg}">{rate}</td></tr>'
    h += '</table>'
    return h


def build_country_table(df_geo):
    rows = []
    for country, sub in df_geo.groupby('endcustomercountry'):
        if country in ('', 'nan'):
            continue
        k = compute_kpis(sub)
        rows.append((country, k))
    rows.sort(key=lambda x: -x[1]['total'])
    rows = rows[:10]
    if not rows:
        return '<p><em>No country data available.</em></p>'

    h = ('<table><tr><th>Country</th>'
         '<th style="text-align:right">Configs</th>'
         '<th style="text-align:right">Coverage</th>'
         '<th style="text-align:right">AI Coverage</th>'
         '<th style="text-align:right">Attach</th>'
         '<th style="text-align:right">Acceptance</th>'
         '<th style="text-align:right">Change</th>'
         '<th style="text-align:right">Att. Failure</th>'
         '</tr>')
    for country, k in rows:
        h += (f'<tr><td><strong>{country}</strong></td>'
              f'<td class="num">{fc(k["total"])}</td>'
              + pct_cell(k['coverage_pct'], 'coverage')
              + f'<td class="num">{fp(k["ai_pct"])}</td>'
              + pct_cell(k['attach_pct'], 'attach')
              + pct_cell(k['acceptance_pct'], 'acceptance')
              + pct_cell(k['change_pct'], 'change')
              + pct_cell(k['att_fail_pct'], 'att_fail')
              + '</tr>')
    h += '</table>'
    return h


def build_rec_overview(df_geo):
    ai = df_geo[df_geo['is_ai']]
    if len(ai) == 0:
        return '<p><em>No AI-recommended rows in this GEO.</em></p>'
    changed = ai[ai['is_changed']]
    n_ai = len(ai)
    n_chg = len(changed)

    def dist_table(series, total, title):
        counts = series[series.isin(['', 'nan']) == False].value_counts()
        if counts.empty:
            return f'<div><h4>{title}</h4><p style="color:#888;font-size:12px"><em>No data.</em></p></div>'
        h = (f'<div><h4>{title}</h4>'
             '<table><tr><th>Value</th><th style="text-align:right">Count</th>'
             '<th style="text-align:right">Share</th></tr>')
        for val, cnt in counts.head(8).items():
            h += f'<tr><td>{val}</td><td class="num">{fc(cnt)}</td><td class="num">{fp(cnt/total*100)}</td></tr>'
        h += '</table></div>'
        return h

    h = f'<p style="font-size:13px;color:#555;margin-bottom:12px">AI rows: <strong>{fc(n_ai)}</strong> &nbsp;|&nbsp; Changed: <strong>{fc(n_chg)}</strong> ({fp(n_chg/n_ai*100) if n_ai else "—"})</p>'
    h += '<div class="grid2">'
    h += dist_table(ai['default_term'],      n_ai,  'AI Recommended — Contract Term')
    h += dist_table(changed['selection_term'] if n_chg else pd.Series(dtype=str),
                    n_chg, 'Rep Selection Term (when changed)')
    h += '</div>'
    h += '<div class="grid2" style="margin-top:16px">'
    h += dist_table(ai['default_servicetype'],      n_ai,  'AI Recommended — Service Type')
    h += dist_table(changed['selection_servicetype'] if n_chg else pd.Series(dtype=str),
                    n_chg, 'Rep Selection Service Type (when changed)')
    h += '</div>'
    return h


def build_coverage_gap(df_geo):
    rows = []
    for (c1, c2), sub in df_geo.groupby(['category1', 'category2']):
        if c1 in ('', 'nan') and c2 in ('', 'nan'):
            continue
        n = len(sub)
        if n < MIN_VOL_CAT:
            continue
        nd = int(sub['no_default'].sum())
        sold_nd = int((sub['no_default'] & sub['has_sold']).sum())
        rows.append({'c1': c1, 'c2': c2, 'n': n, 'nd': nd,
                     'nd_pct': nd / n * 100, 'sold_nd': sold_nd})
    rows.sort(key=lambda x: -x['nd_pct'])

    if not rows:
        return '<p><em>No category data available.</em></p>'

    h = ('<table><tr><th>Category 1</th><th>Category 2</th>'
         '<th style="text-align:right">Configs</th>'
         '<th style="text-align:right">No Default</th>'
         '<th style="text-align:right">No Default Rate</th>'
         '<th style="text-align:right">Sold w/o Rec.</th></tr>')
    for r in rows[:12]:
        h += (f'<tr><td>{r["c1"]}</td><td>{r["c2"]}</td>'
              f'<td class="num">{fc(r["n"])}</td>'
              f'<td class="num">{fc(r["nd"])}</td>'
              + pct_cell(r['nd_pct'], 'no_default')
              + f'<td class="num">{fc(r["sold_nd"])}</td></tr>')
    h += '</table>'

    # Machine types with high no-default AND active sales
    mt_rows = []
    for mt, sub in df_geo.groupby('machinetype'):
        if mt in ('', 'nan'):
            continue
        n = len(sub)
        if n < MIN_VOL_CAT:
            continue
        nd = int(sub['no_default'].sum())
        sold_nd = int((sub['no_default'] & sub['has_sold']).sum())
        if sold_nd < 5:
            continue
        mt_rows.append({'mt': mt, 'n': n,
                        'nd_pct': nd / n * 100, 'sold_nd': sold_nd})
    mt_rows.sort(key=lambda x: -x['sold_nd'])

    if mt_rows:
        h += '<h4>Top Machine Types — High Coverage Gap with Active Sales</h4>'
        h += ('<table><tr><th>Machine Type</th>'
              '<th style="text-align:right">Configs</th>'
              '<th style="text-align:right">No Default Rate</th>'
              '<th style="text-align:right">Sold w/o Rec.</th></tr>')
        for r in mt_rows[:10]:
            h += (f'<tr><td><code>{r["mt"]}</code></td>'
                  f'<td class="num">{fc(r["n"])}</td>'
                  + pct_cell(r['nd_pct'], 'no_default')
                  + f'<td class="num">{fc(r["sold_nd"])}</td></tr>')
        h += '</table>'
    return h


def build_low_acceptance(df_geo):
    rows = []
    for (c1, c2), sub in df_geo.groupby(['category1', 'category2']):
        if c1 in ('', 'nan') and c2 in ('', 'nan'):
            continue
        defaults = int(sub['has_default'].sum())
        if defaults < MIN_VOL_CAT:
            continue
        accepted = int(sub['is_accepted'].sum())
        changed  = int(sub['is_changed'].sum())
        rows.append({'c1': c1, 'c2': c2, 'defaults': defaults,
                     'accepted': accepted, 'changed': changed,
                     'acc_pct': accepted / defaults * 100,
                     'chg_pct': changed  / defaults * 100})
    rows.sort(key=lambda x: -x['chg_pct'])

    if not rows:
        return '<p><em>No category data available.</em></p>'

    h = ('<table><tr><th>Category 1</th><th>Category 2</th>'
         '<th style="text-align:right">Defaults</th>'
         '<th style="text-align:right">Accepted</th>'
         '<th style="text-align:right">Acceptance Rate</th>'
         '<th style="text-align:right">Changed</th>'
         '<th style="text-align:right">Change Rate</th></tr>')
    for r in rows[:12]:
        h += (f'<tr><td>{r["c1"]}</td><td>{r["c2"]}</td>'
              f'<td class="num">{fc(r["defaults"])}</td>'
              f'<td class="num">{fc(r["accepted"])}</td>'
              + pct_cell(r['acc_pct'], 'acceptance')
              + f'<td class="num">{fc(r["changed"])}</td>'
              + pct_cell(r['chg_pct'], 'change')
              + '</tr>')
    h += '</table>'

    # Machine types with high change rate
    mt_rows = []
    for mt, sub in df_geo[df_geo['has_default']].groupby('machinetype'):
        if mt in ('', 'nan'):
            continue
        defaults = len(sub)
        if defaults < MIN_VOL_MT:
            continue
        accepted = int(sub['is_accepted'].sum())
        changed  = int(sub['is_changed'].sum())
        mt_rows.append({'mt': mt, 'defaults': defaults,
                        'acc_pct': accepted / defaults * 100,
                        'chg_pct': changed  / defaults * 100})
    mt_rows.sort(key=lambda x: -x['chg_pct'])

    if mt_rows:
        h += f'<h4>Top Machine Types — High Change Rate (min {MIN_VOL_MT} defaults)</h4>'
        h += ('<table><tr><th>Machine Type</th>'
              '<th style="text-align:right">Defaults</th>'
              '<th style="text-align:right">Acceptance Rate</th>'
              '<th style="text-align:right">Change Rate</th></tr>')
        for r in mt_rows[:10]:
            h += (f'<tr><td><code>{r["mt"]}</code></td>'
                  f'<td class="num">{fc(r["defaults"])}</td>'
                  + pct_cell(r['acc_pct'], 'acceptance')
                  + pct_cell(r['chg_pct'], 'change')
                  + '</tr>')
        h += '</table>'
    return h


def build_att_failure(df_geo):
    rows = []
    for (c1, c2), sub in df_geo.groupby(['category1', 'category2']):
        if c1 in ('', 'nan') and c2 in ('', 'nan'):
            continue
        defaults = int(sub['has_default'].sum())
        if defaults < MIN_VOL_CAT:
            continue
        att_fail = int(sub['att_failure'].sum())
        rows.append({'c1': c1, 'c2': c2, 'defaults': defaults,
                     'att_fail': att_fail,
                     'att_fail_pct': att_fail / defaults * 100})
    rows.sort(key=lambda x: -x['att_fail_pct'])

    if not rows:
        return '<p><em>No category data available.</em></p>'

    h = ('<table><tr><th>Category 1</th><th>Category 2</th>'
         '<th style="text-align:right">Defaults</th>'
         '<th style="text-align:right">Att. Failures</th>'
         '<th style="text-align:right">Failure Rate</th></tr>')
    for r in rows[:12]:
        h += (f'<tr><td>{r["c1"]}</td><td>{r["c2"]}</td>'
              f'<td class="num">{fc(r["defaults"])}</td>'
              f'<td class="num">{fc(r["att_fail"])}</td>'
              + pct_cell(r['att_fail_pct'], 'att_fail')
              + '</tr>')
    h += '</table>'

    # By country
    ct_rows = []
    for country, sub in df_geo.groupby('endcustomercountry'):
        if country in ('', 'nan'):
            continue
        defaults = int(sub['has_default'].sum())
        if defaults < MIN_VOL_CAT:
            continue
        att_fail = int(sub['att_failure'].sum())
        ct_rows.append({'country': country, 'defaults': defaults,
                        'att_fail': att_fail,
                        'att_fail_pct': att_fail / defaults * 100})
    ct_rows.sort(key=lambda x: -x['att_fail_pct'])

    if ct_rows:
        h += '<h4>Attachment Failure by Country (top 10, min 20 defaults)</h4>'
        h += ('<table><tr><th>Country</th>'
              '<th style="text-align:right">Defaults</th>'
              '<th style="text-align:right">Att. Failures</th>'
              '<th style="text-align:right">Failure Rate</th></tr>')
        for r in ct_rows[:10]:
            h += (f'<tr><td><strong>{r["country"]}</strong></td>'
                  f'<td class="num">{fc(r["defaults"])}</td>'
                  f'<td class="num">{fc(r["att_fail"])}</td>'
                  + pct_cell(r['att_fail_pct'], 'att_fail')
                  + '</tr>')
        h += '</table>'
    return h


def build_trend(df_geo):
    months = sorted(m for m in df_geo['year_month'].unique() if m is not None)
    rows = []
    for ym in months:
        sub = df_geo[df_geo['year_month'] == ym]
        if len(sub) < 10:
            continue
        k = compute_kpis(sub)
        rows.append({'month': str(ym), **k})

    if not rows:
        return '<p><em>Insufficient monthly data for trend analysis.</em></p>'

    h = ('<table><tr><th>Month</th>'
         '<th style="text-align:right">Configs</th>'
         '<th style="text-align:right">Coverage</th>'
         '<th style="text-align:right">AI Coverage</th>'
         '<th style="text-align:right">Attach</th>'
         '<th style="text-align:right">Acceptance</th>'
         '<th style="text-align:right">Change</th>'
         '<th style="text-align:right">Influence</th>'
         '<th style="text-align:right">Att. Failure</th>'
         '</tr>')
    for r in rows:
        h += (f'<tr><td><strong>{r["month"]}</strong></td>'
              f'<td class="num">{fc(r["total"])}</td>'
              + pct_cell(r['coverage_pct'],   'coverage')
              + f'<td class="num">{fp(r["ai_pct"])}</td>'
              + pct_cell(r['attach_pct'],     'attach')
              + pct_cell(r['acceptance_pct'], 'acceptance')
              + pct_cell(r['change_pct'],     'change')
              + f'<td class="num">{fp(r["influence_pct"])}</td>'
              + pct_cell(r['att_fail_pct'],   'att_fail')
              + '</tr>')
    h += '</table>'
    return h


# ── GEO SECTION ────────────────────────────────────────────────────────────────
def build_geo_section(df, geo):
    start = GEO_START[geo]
    df_geo = df[(df['geo'] == geo) & (df['contract_creation_date'] >= start)]
    k = compute_kpis(df_geo)
    start_str = start.strftime('%Y-%m-%d')
    print(f'  {geo}: n={len(df_geo):,} (from {start_str})  '
          f'coverage={fp(k["coverage_pct"])}  '
          f'acceptance={fp(k["acceptance_pct"])}', flush=True)

    s = (f'<div class="section" id="{geo}">'
         f'<div class="section-header"><h2>{GEO_FULL[geo]}</h2></div>'
         f'<div class="section-body">')

    s += (f'<div class="subsection"><h3>A. Operational KPI Dashboard</h3>'
          f'<p class="insight">&#9432; Analysis period starts from go-live date: '
          f'<strong>{start_str}</strong>. Total configurations in scope: <strong>{fc(len(df_geo))}</strong>.</p>'
          + LEGEND + build_kpi_table(k) + '</div>')

    s += ('<div class="subsection"><h3>B. Country Drill-Down (Top 10 by Volume)</h3>'
          + LEGEND + build_country_table(df_geo) + '</div>')

    s += (f'<div class="subsection"><h3>C. Recommendation Profile (AI Rows Only)</h3>'
          f'<p class="insight">AI-recommended rows: <strong>{fc(k["ai_count"])}</strong> '
          f'({fp(k["ai_pct"])} of all configs). Shows what the model recommends and '
          f'what reps select when they deviate &mdash; reveals term or service-type mismatches.</p>'
          + build_rec_overview(df_geo) + '</div>')

    s += ('<div class="subsection"><h3>D. Improvement Area 1 &mdash; Coverage Gaps (No Default)</h3>'
          '<p class="insight">Segments where the AI has no recommendation but service is still '
          'sold. These are prime expansion targets &mdash; adding coverage here could directly '
          'lift attach rates.</p>'
          + build_coverage_gap(df_geo) + '</div>')

    s += ('<div class="subsection"><h3>E. Improvement Area 2 &mdash; Low Acceptance Segments '
          '(High Change Rate)</h3>'
          '<p class="insight">Segments where reps frequently override the AI recommendation. '
          'High change rate signals the model\'s default PN does not match market preference '
          '&mdash; these segments need model retraining or data refresh.</p>'
          + build_low_acceptance(df_geo) + '</div>')

    s += ('<div class="subsection"><h3>F. Improvement Area 3 &mdash; Attachment Failures '
          '(Shown but Not Sold)</h3>'
          '<p class="insight">Segments where the AI shows a recommendation but the rep sells '
          'no service at all. The model is present but not driving conversion &mdash; may need '
          'a stronger default PN, pricing signal, or rep coaching.</p>'
          + build_att_failure(df_geo) + '</div>')

    s += ('<div class="subsection"><h3>G. Improvement Area 4 &mdash; Monthly Trend</h3>'
          '<p class="insight">Monthly acceptance, attach, and AI coverage rates. '
          'Rising acceptance signals the model is improving; a sustained downward trend '
          'warrants investigation of recent model changes or data drift.</p>'
          + LEGEND + build_trend(df_geo) + '</div>')

    s += '</div></div>'
    return s


# ── EXECUTIVE SUMMARY ──────────────────────────────────────────────────────────
def build_exec_summary(df):
    s = ('<div class="section" id="summary">'
         '<div class="section-header"><h2>Executive Summary &mdash; Global Overview</h2></div>'
         '<div class="section-body">')

    # KPI cards
    s += '<div class="card-grid">'
    for geo in GEOS:
        start = GEO_START[geo]
        sub = df[(df['geo'] == geo) & (df['contract_creation_date'] >= start)]
        k = compute_kpis(sub)
        acc = k['acceptance_pct']
        col = ('#2e7d32' if (acc >= 55 or np.isnan(acc)) else
               '#f57f17' if acc >= 45 else '#c62828')
        s += (f'<div class="kpi-card">'
              f'<div class="geo-tag">{geo}</div>'
              f'<div class="label">Acceptance Rate</div>'
              f'<div class="big" style="color:{col}">{fp(acc)}</div>'
              f'<div class="sub">{fc(k["total"])} configs &nbsp;|&nbsp; '
              f'{fp(k["coverage_pct"])} coverage</div>'
              f'<div class="sub" style="margin-top:3px;color:#aaa">from {start.strftime("%Y-%m-%d")}</div>'
              f'</div>')
    s += '</div>'

    # Cross-GEO table
    s += '<h3 style="font-size:14px;font-weight:600;color:#37474f;margin-bottom:10px;border-left:4px solid #42a5f5;padding-left:10px">Cross-GEO KPI Comparison (post go-live)</h3>'
    s += '<p class="insight">&#9432; Each GEO filtered from its own go-live date: EMEA from 2025-09-28, AP / LA / NA from 2025-11-28.</p>'
    s += LEGEND
    s += ('<table><tr><th>GEO</th>'
          '<th style="text-align:right">Analysis From</th>'
          '<th style="text-align:right">Configs</th>'
          '<th style="text-align:right">Coverage</th>'
          '<th style="text-align:right">AI Coverage</th>'
          '<th style="text-align:right">Attach</th>'
          '<th style="text-align:right">Acceptance</th>'
          '<th style="text-align:right">Change</th>'
          '<th style="text-align:right">Influence</th>'
          '<th style="text-align:right">Att. Failure</th>'
          '</tr>')
    for geo in GEOS:
        start = GEO_START[geo]
        sub = df[(df['geo'] == geo) & (df['contract_creation_date'] >= start)]
        k = compute_kpis(sub)
        s += (f'<tr><td><strong>{geo}</strong></td>'
              f'<td class="num">{start.strftime("%Y-%m-%d")}</td>'
              f'<td class="num">{fc(k["total"])}</td>'
              + pct_cell(k['coverage_pct'],   'coverage')
              + f'<td class="num">{fp(k["ai_pct"])}</td>'
              + pct_cell(k['attach_pct'],     'attach')
              + pct_cell(k['acceptance_pct'], 'acceptance')
              + pct_cell(k['change_pct'],     'change')
              + f'<td class="num">{fp(k["influence_pct"])}</td>'
              + pct_cell(k['att_fail_pct'],   'att_fail')
              + '</tr>')
    s += '</table>'
    s += '</div></div>'
    return s


# ── FULL HTML ──────────────────────────────────────────────────────────────────
def build_html(df, d_min, d_max):
    period    = f'{d_min.strftime("%Y-%m-%d")} to {d_max.strftime("%Y-%m-%d")}'
    generated = datetime.now().strftime('%Y-%m-%d %H:%M')

    nav_links = ''.join(
        f'<a href="#{g}">{g}</a>' for g in GEOS)

    navbar = (f'<nav class="navbar">'
              f'<span class="brand">Service Smart Recommendation &mdash; Operational KPI Report</span>'
              f'<a href="#summary">Executive Summary</a>'
              f'{nav_links}'
              f'<span class="meta">Period: {period} &nbsp;|&nbsp; Generated: {generated}</span>'
              f'</nav>')

    print('Building Executive Summary...', flush=True)
    body_parts = [build_exec_summary(df)]
    print('Building GEO sections...', flush=True)
    for geo in GEOS:
        body_parts.append(build_geo_section(df, geo))

    return (f'<!DOCTYPE html>\n<html lang="en">\n<head>\n'
            f'<meta charset="UTF-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1.0">'
            f'<title>Service Smart — Operational KPI Report</title>\n'
            f'{STYLE}\n</head>\n<body>\n'
            f'{navbar}\n'
            f'<div class="page">\n'
            + '\n'.join(body_parts)
            + '\n</div>\n</body>\n</html>')


# ── MAIN ───────────────────────────────────────────────────────────────────────
def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    df, d_min, d_max = load_data()
    html = build_html(df, d_min, d_max)
    with open(OUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'\n[Done] Report saved to: {OUT_FILE}', flush=True)


if __name__ == '__main__':
    main()
