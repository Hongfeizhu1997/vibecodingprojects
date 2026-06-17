#!/usr/bin/env python3
"""
Service Smart Recommendation — Operational KPI Report (Excel source)
Sources : Ai_Report_20250815~20260306.xlsx  (rows with create date up to 2026-03-16)
          Ai_Report_2026-04-01(3.17-4.01).xlsx  (rows from 2026-03-17 onwards)
Output  : validation_output/operational_kpi_report_excel.html

Column mapping (Excel → meaning):
  geo                  → geographic region
  country              → country code
  configuredFrom       → New CTO / Copied CTO
  defaultFrom          → 'AI' if AI-sourced recommendation
  defaultServicePn1    → recommended service PN  (= default_pn in CSV)
  defaultServicePn1Desc→ recommended service description
  selectedServicePn1   → service PN actually sold (= selection_pn in CSV)
  selectedServicePn1Desc → sold service description
  selectedFrom         → 'GBB(Default)' / 'Non-Default' / blank

Metric definitions (same as validated definitions in validate.py):
  Defaults        = defaultServicePn1 not blank
  Default & sold  = Defaults AND selectedServicePn1 not blank
  Accepted        = Defaults AND selectedServicePn1 == defaultServicePn1
  Changed         = Default & sold  -  Accepted
  Att. Failure    = Defaults AND selectedServicePn1 blank

Go-live filters applied:
  EMEA  → 2025-09-28  (whole-GEO go-live; FR/ES/DK pilot from 2025-08-15)
  AP / LA / NA → 2025-11-28
"""

import pandas as pd
import numpy as np
import os
import warnings
from datetime import datetime

warnings.filterwarnings('ignore')

# ── CONFIG ─────────────────────────────────────────────────────────────────────
FILE_OLD = 'Ai_Report_20250815~20260306.xlsx'
FILE_NEW = 'Ai_Report_2026-04-01(3.17-4.01).xlsx'
OUT_DIR  = 'validation_output'
OUT_FILE = os.path.join(OUT_DIR, 'operational_kpi_report_excel.html')

GEOS = ['EMEA', 'AP', 'LA', 'NA']
GEO_FULL = {
    'EMEA': 'EMEA — Europe, Middle East &amp; Africa',
    'AP':   'AP — Asia-Pacific',
    'LA':   'LA — Latin America',
    'NA':   'NA — North America',
}
GEO_START = {
    'EMEA': pd.Timestamp('2025-09-28'),
    'AP':   pd.Timestamp('2025-11-28'),
    'LA':   pd.Timestamp('2025-11-28'),
    'NA':   pd.Timestamp('2025-11-28'),
}
MIN_VOL = 20   # minimum defaults for country-level analysis

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
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return '—'
    return f'{float(v):.{d}f}%'


def fc(v):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return '—'
    return f'{int(v):,}'


def pct_cell(v, metric):
    bg = color_for(metric, v)
    return f'<td class="num" style="background:{bg}">{fp(v)}</td>'


# ── DATA LOADING ───────────────────────────────────────────────────────────────
KEEP_COLS = [
    'configuredFrom', 'geo', 'country', 'defaultFrom',
    'defaultServicePn1', 'defaultServicePn1Desc',
    'selectedFrom', 'selectedServicePn1', 'selectedServicePn1Desc',
]

def load_data():
    print(f'Loading {FILE_OLD} ...', flush=True)
    df_old = pd.read_excel(FILE_OLD, sheet_name='Ai-Report', engine='openpyxl',
                           keep_default_na=False)
    df_old.columns = df_old.columns.str.strip()
    df_old['_date'] = pd.to_datetime(df_old['create date'], errors='coerce')
    # keep rows up to Mar 16 to avoid overlap with new file
    df_old = df_old[df_old['_date'] <= pd.Timestamp('2026-03-16')]
    df_old = df_old[KEEP_COLS + ['_date']].copy()
    print(f'  Old file rows in scope : {len(df_old):,}  '
          f'({df_old["_date"].min().date()} – {df_old["_date"].max().date()})', flush=True)

    print(f'Loading {FILE_NEW} ...', flush=True)
    df_new = pd.read_excel(FILE_NEW, sheet_name='Ai-Report', engine='openpyxl',
                           keep_default_na=False)
    df_new.columns = df_new.columns.str.strip()
    df_new['_date'] = pd.to_datetime(df_new['createdDate'], utc=True,
                                     errors='coerce').dt.tz_localize(None)
    df_new = df_new[df_new['_date'] >= pd.Timestamp('2026-03-17')]
    df_new = df_new[KEEP_COLS + ['_date']].copy()
    print(f'  New file rows in scope : {len(df_new):,}  '
          f'({df_new["_date"].min().date()} – {df_new["_date"].max().date()})', flush=True)

    df = pd.concat([df_old, df_new], ignore_index=True)

    # Normalise strings
    str_cols = ['configuredFrom', 'geo', 'country', 'defaultFrom',
                'defaultServicePn1', 'defaultServicePn1Desc',
                'selectedFrom', 'selectedServicePn1', 'selectedServicePn1Desc']
    for col in str_cols:
        df[col] = df[col].astype(str).str.strip()

    # Metric flags
    df['has_default']  = df['defaultServicePn1'] != ''
    df['is_ai']        = df['defaultFrom'] == 'AI'
    df['has_sold']     = df['selectedServicePn1'] != ''
    df['def_and_sold'] = df['has_default'] & df['has_sold']
    df['is_accepted']  = (df['has_default'] &
                          (df['selectedServicePn1'] == df['defaultServicePn1']))
    df['is_changed']   = df['def_and_sold'] & ~df['is_accepted']
    df['no_default']   = ~df['has_default']
    df['att_failure']  = df['has_default'] & ~df['has_sold']

    # Year-month for trend
    df['year_month'] = (df['_date'].dt.to_period('M')
                        .astype('object')
                        .where(df['_date'].notna(), other=None))

    d_min = df['_date'].min()
    d_max = df['_date'].max()
    print(f'  Combined total rows    : {len(df):,}  '
          f'({d_min.date()} – {d_max.date()})', flush=True)
    print(f'  GEO breakdown          : {df["geo"].value_counts().to_dict()}', flush=True)
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


# ── STYLE ──────────────────────────────────────────────────────────────────────
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
.tag-cf{display:inline-block;background:#e8eaf6;color:#3949ab;border-radius:3px;
        padding:1px 6px;font-size:11px;font-weight:600}
</style>
"""

LEGEND = """<div class="legend">
  <span style="background:#c8e6c9;color:#1b5e20">&#9679; Good</span>
  <span style="background:#fff9c4;color:#f57f17">&#9679; Moderate</span>
  <span style="background:#ffcdd2;color:#b71c1c">&#9679; Needs attention</span>
</div>"""


# ── SECTION BUILDERS ───────────────────────────────────────────────────────────

def build_kpi_table(k):
    rows = [
        ('Total Configurations',                      fc(k['total']),    '—',                  None,         None),
        ('Default Coverage (any default shown)',       fc(k['defaults']), fp(k['coverage_pct']),  'coverage',   k['coverage_pct']),
        ('AI Coverage (AI-sourced default)',           fc(k['ai_count']), fp(k['ai_pct']),         None,         None),
        ('Service Attach Rate',                        fc(k['def_sold']), fp(k['attach_pct']),     'attach',     k['attach_pct']),
        ('Acceptance Rate (rep kept default)',         fc(k['accepted']), fp(k['acceptance_pct']), 'acceptance', k['acceptance_pct']),
        ('Change Rate (rep overrode default)',         fc(k['changed']),  fp(k['change_pct']),     'change',     k['change_pct']),
        ('Influence Rate (accepted+changed)/defaults', fc(k['def_sold']), fp(k['influence_pct']),  None,         None),
        ('Attachment Failure (shown, nothing sold)',   fc(k['att_fail']), fp(k['att_fail_pct']),   'att_fail',   k['att_fail_pct']),
        ('No Default (no recommendation available)',  fc(k['no_default']),fp(k['no_default_pct']),'no_default', k['no_default_pct']),
    ]
    h = ('<table><tr><th>Metric</th>'
         '<th style="text-align:right">Count</th>'
         '<th style="text-align:right">Rate</th></tr>')
    for label, cnt, rate, mtype, mval in rows:
        bg = f'background:{color_for(mtype, mval)};' if mtype else ''
        h += (f'<tr><td>{label}</td>'
              f'<td class="num">{cnt}</td>'
              f'<td class="num" style="{bg}">{rate}</td></tr>')
    h += '</table>'
    return h


def build_cf_breakdown(df_geo):
    """KPIs split by configuredFrom (New CTO / Copied CTO / All)."""
    groups = [
        ('All configurations', df_geo),
        ('New CTO only',       df_geo[df_geo['configuredFrom'] == 'New CTO']),
        ('Copied CTO only',    df_geo[df_geo['configuredFrom'] == 'Copied CTO']),
    ]
    h = ('<table><tr><th>Config Origin</th>'
         '<th style="text-align:right">Configs</th>'
         '<th style="text-align:right">Coverage</th>'
         '<th style="text-align:right">AI Coverage</th>'
         '<th style="text-align:right">Attach</th>'
         '<th style="text-align:right">Acceptance</th>'
         '<th style="text-align:right">Change</th>'
         '<th style="text-align:right">Influence</th>'
         '<th style="text-align:right">Att. Failure</th>'
         '</tr>')
    for label, sub in groups:
        if len(sub) == 0:
            continue
        k = compute_kpis(sub)
        h += (f'<tr><td><span class="tag-cf">{label}</span></td>'
              f'<td class="num">{fc(k["total"])}</td>'
              + pct_cell(k['coverage_pct'],   'coverage')
              + f'<td class="num">{fp(k["ai_pct"])}</td>'
              + pct_cell(k['attach_pct'],     'attach')
              + pct_cell(k['acceptance_pct'], 'acceptance')
              + pct_cell(k['change_pct'],     'change')
              + f'<td class="num">{fp(k["influence_pct"])}</td>'
              + pct_cell(k['att_fail_pct'],   'att_fail')
              + '</tr>')
    h += '</table>'
    return h


def build_country_table(df_geo):
    rows = []
    for country, sub in df_geo.groupby('country'):
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
              + pct_cell(k['coverage_pct'],   'coverage')
              + f'<td class="num">{fp(k["ai_pct"])}</td>'
              + pct_cell(k['attach_pct'],     'attach')
              + pct_cell(k['acceptance_pct'], 'acceptance')
              + pct_cell(k['change_pct'],     'change')
              + pct_cell(k['att_fail_pct'],   'att_fail')
              + '</tr>')
    h += '</table>'
    return h


def build_rec_overview(df_geo):
    """Top recommended PNs/descriptions vs what reps choose when they change."""
    ai = df_geo[df_geo['is_ai']]
    if len(ai) == 0:
        return '<p><em>No AI-recommended rows in this GEO.</em></p>'
    changed = ai[ai['is_changed']]
    n_ai  = len(ai)
    n_chg = len(changed)

    def top_table(series, total, title, col_label='Description'):
        counts = series[(series != '') & (series != 'nan')].value_counts()
        if counts.empty:
            return f'<div><h4>{title}</h4><p style="color:#888;font-size:12px"><em>No data.</em></p></div>'
        h = (f'<div><h4>{title}</h4>'
             f'<table><tr><th>{col_label}</th>'
             f'<th style="text-align:right">Count</th>'
             f'<th style="text-align:right">Share</th></tr>')
        for val, cnt in counts.head(8).items():
            # truncate long descriptions
            display = (val[:70] + '…') if len(val) > 70 else val
            h += (f'<tr><td title="{val}">{display}</td>'
                  f'<td class="num">{fc(cnt)}</td>'
                  f'<td class="num">{fp(cnt/total*100)}</td></tr>')
        h += '</table></div>'
        return h

    h = (f'<p style="font-size:13px;color:#555;margin-bottom:12px">'
         f'AI rows: <strong>{fc(n_ai)}</strong> &nbsp;|&nbsp; '
         f'Changed: <strong>{fc(n_chg)}</strong> ({fp(n_chg/n_ai*100) if n_ai else "—"})</p>')

    h += '<div class="grid2">'
    h += top_table(ai['defaultServicePn1Desc'], n_ai,
                   'AI Recommended — Top Service Descriptions')
    h += top_table(changed['selectedServicePn1Desc'] if n_chg else pd.Series(dtype=str),
                   n_chg, 'Rep Selection — Top Descriptions (when changed)')
    h += '</div>'
    return h


def build_coverage_gap(df_geo):
    """Coverage gap by country and configuredFrom."""
    # By country
    ct_rows = []
    for country, sub in df_geo.groupby('country'):
        if country in ('', 'nan'):
            continue
        n = len(sub)
        if n < MIN_VOL:
            continue
        nd = int(sub['no_default'].sum())
        sold_nd = int((sub['no_default'] & sub['has_sold']).sum())
        ct_rows.append({'country': country, 'n': n,
                        'nd': nd, 'nd_pct': nd / n * 100, 'sold_nd': sold_nd})
    ct_rows.sort(key=lambda x: -x['nd_pct'])

    h = '<h4>Coverage Gap by Country (sorted by No-Default Rate)</h4>'
    if ct_rows:
        h += ('<table><tr><th>Country</th>'
              '<th style="text-align:right">Configs</th>'
              '<th style="text-align:right">No Default</th>'
              '<th style="text-align:right">No Default Rate</th>'
              '<th style="text-align:right">Sold w/o Rec.</th></tr>')
        for r in ct_rows[:15]:
            h += (f'<tr><td><strong>{r["country"]}</strong></td>'
                  f'<td class="num">{fc(r["n"])}</td>'
                  f'<td class="num">{fc(r["nd"])}</td>'
                  + pct_cell(r['nd_pct'], 'no_default')
                  + f'<td class="num">{fc(r["sold_nd"])}</td></tr>')
        h += '</table>'
    else:
        h += '<p><em>No country data available.</em></p>'

    # By configuredFrom
    h += '<h4>Coverage Gap by Config Origin</h4>'
    cf_rows = []
    for cf, sub in df_geo.groupby('configuredFrom'):
        if cf in ('', 'nan'):
            continue
        n = len(sub)
        if n < 5:
            continue
        nd = int(sub['no_default'].sum())
        sold_nd = int((sub['no_default'] & sub['has_sold']).sum())
        cf_rows.append({'cf': cf, 'n': n,
                        'nd': nd, 'nd_pct': nd / n * 100, 'sold_nd': sold_nd})
    if cf_rows:
        h += ('<table><tr><th>Config Origin</th>'
              '<th style="text-align:right">Configs</th>'
              '<th style="text-align:right">No Default</th>'
              '<th style="text-align:right">No Default Rate</th>'
              '<th style="text-align:right">Sold w/o Rec.</th></tr>')
        for r in sorted(cf_rows, key=lambda x: -x['nd_pct']):
            h += (f'<tr><td><span class="tag-cf">{r["cf"]}</span></td>'
                  f'<td class="num">{fc(r["n"])}</td>'
                  f'<td class="num">{fc(r["nd"])}</td>'
                  + pct_cell(r['nd_pct'], 'no_default')
                  + f'<td class="num">{fc(r["sold_nd"])}</td></tr>')
        h += '</table>'
    return h


def build_low_acceptance(df_geo):
    """Low acceptance (high change rate) by country and configuredFrom."""
    # By country
    ct_rows = []
    for country, sub in df_geo.groupby('country'):
        if country in ('', 'nan'):
            continue
        defaults = int(sub['has_default'].sum())
        if defaults < MIN_VOL:
            continue
        accepted = int(sub['is_accepted'].sum())
        changed  = int(sub['is_changed'].sum())
        ct_rows.append({'country': country, 'defaults': defaults,
                        'accepted': accepted, 'changed': changed,
                        'acc_pct': accepted / defaults * 100,
                        'chg_pct': changed  / defaults * 100})
    ct_rows.sort(key=lambda x: -x['chg_pct'])

    h = '<h4>Acceptance &amp; Change Rate by Country</h4>'
    if ct_rows:
        h += ('<table><tr><th>Country</th>'
              '<th style="text-align:right">Defaults</th>'
              '<th style="text-align:right">Accepted</th>'
              '<th style="text-align:right">Acceptance Rate</th>'
              '<th style="text-align:right">Changed</th>'
              '<th style="text-align:right">Change Rate</th></tr>')
        for r in ct_rows[:15]:
            h += (f'<tr><td><strong>{r["country"]}</strong></td>'
                  f'<td class="num">{fc(r["defaults"])}</td>'
                  f'<td class="num">{fc(r["accepted"])}</td>'
                  + pct_cell(r['acc_pct'], 'acceptance')
                  + f'<td class="num">{fc(r["changed"])}</td>'
                  + pct_cell(r['chg_pct'], 'change')
                  + '</tr>')
        h += '</table>'
    else:
        h += '<p><em>No country data available.</em></p>'

    # By configuredFrom
    h += '<h4>Acceptance &amp; Change Rate by Config Origin</h4>'
    cf_rows = []
    for cf, sub in df_geo.groupby('configuredFrom'):
        if cf in ('', 'nan'):
            continue
        defaults = int(sub['has_default'].sum())
        if defaults < 5:
            continue
        accepted = int(sub['is_accepted'].sum())
        changed  = int(sub['is_changed'].sum())
        cf_rows.append({'cf': cf, 'defaults': defaults,
                        'accepted': accepted, 'changed': changed,
                        'acc_pct': accepted / defaults * 100,
                        'chg_pct': changed  / defaults * 100})
    if cf_rows:
        h += ('<table><tr><th>Config Origin</th>'
              '<th style="text-align:right">Defaults</th>'
              '<th style="text-align:right">Accepted</th>'
              '<th style="text-align:right">Acceptance Rate</th>'
              '<th style="text-align:right">Changed</th>'
              '<th style="text-align:right">Change Rate</th></tr>')
        for r in sorted(cf_rows, key=lambda x: -x['chg_pct']):
            h += (f'<tr><td><span class="tag-cf">{r["cf"]}</span></td>'
                  f'<td class="num">{fc(r["defaults"])}</td>'
                  f'<td class="num">{fc(r["accepted"])}</td>'
                  + pct_cell(r['acc_pct'], 'acceptance')
                  + f'<td class="num">{fc(r["changed"])}</td>'
                  + pct_cell(r['chg_pct'], 'change')
                  + '</tr>')
        h += '</table>'
    return h


def build_att_failure(df_geo):
    """Attachment failure by country and configuredFrom."""
    # By country
    ct_rows = []
    for country, sub in df_geo.groupby('country'):
        if country in ('', 'nan'):
            continue
        defaults = int(sub['has_default'].sum())
        if defaults < MIN_VOL:
            continue
        att_fail = int(sub['att_failure'].sum())
        ct_rows.append({'country': country, 'defaults': defaults,
                        'att_fail': att_fail,
                        'att_fail_pct': att_fail / defaults * 100})
    ct_rows.sort(key=lambda x: -x['att_fail_pct'])

    h = '<h4>Attachment Failure by Country</h4>'
    if ct_rows:
        h += ('<table><tr><th>Country</th>'
              '<th style="text-align:right">Defaults</th>'
              '<th style="text-align:right">Att. Failures</th>'
              '<th style="text-align:right">Failure Rate</th></tr>')
        for r in ct_rows[:15]:
            h += (f'<tr><td><strong>{r["country"]}</strong></td>'
                  f'<td class="num">{fc(r["defaults"])}</td>'
                  f'<td class="num">{fc(r["att_fail"])}</td>'
                  + pct_cell(r['att_fail_pct'], 'att_fail')
                  + '</tr>')
        h += '</table>'
    else:
        h += '<p><em>No country data available.</em></p>'

    # By configuredFrom
    h += '<h4>Attachment Failure by Config Origin</h4>'
    cf_rows = []
    for cf, sub in df_geo.groupby('configuredFrom'):
        if cf in ('', 'nan'):
            continue
        defaults = int(sub['has_default'].sum())
        if defaults < 5:
            continue
        att_fail = int(sub['att_failure'].sum())
        cf_rows.append({'cf': cf, 'defaults': defaults,
                        'att_fail': att_fail,
                        'att_fail_pct': att_fail / defaults * 100})
    if cf_rows:
        h += ('<table><tr><th>Config Origin</th>'
              '<th style="text-align:right">Defaults</th>'
              '<th style="text-align:right">Att. Failures</th>'
              '<th style="text-align:right">Failure Rate</th></tr>')
        for r in sorted(cf_rows, key=lambda x: -x['att_fail_pct']):
            h += (f'<tr><td><span class="tag-cf">{r["cf"]}</span></td>'
                  f'<td class="num">{fc(r["defaults"])}</td>'
                  f'<td class="num">{fc(r["att_fail"])}</td>'
                  + pct_cell(r['att_fail_pct'], 'att_fail')
                  + '</tr>')
        h += '</table>'
    return h


def build_trend(df_geo):
    """Monthly trend table."""
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
    start  = GEO_START[geo]
    df_geo = df[(df['geo'] == geo) & (df['_date'] >= start)]
    k      = compute_kpis(df_geo)
    start_str = start.strftime('%Y-%m-%d')
    print(f'  {geo}: n={len(df_geo):,} (from {start_str})  '
          f'coverage={fp(k["coverage_pct"])}  '
          f'acceptance={fp(k["acceptance_pct"])}', flush=True)

    s = (f'<div class="section" id="{geo}">'
         f'<div class="section-header"><h2>{GEO_FULL[geo]}</h2></div>'
         f'<div class="section-body">')

    # A. KPI Dashboard
    s += (f'<div class="subsection"><h3>A. Operational KPI Dashboard</h3>'
          f'<p class="insight">&#9432; Analysis from go-live date: <strong>{start_str}</strong>. '
          f'Configurations in scope: <strong>{fc(len(df_geo))}</strong>.</p>'
          + LEGEND + build_kpi_table(k) + '</div>')

    # A2. By configuredFrom
    s += ('<div class="subsection"><h3>A2. KPI Breakdown by Config Origin</h3>'
          '<p class="insight">New CTO = rep started from scratch. '
          'Copied CTO = rep copied an existing configuration. '
          'Acceptance rates typically differ between these groups.</p>'
          + LEGEND + build_cf_breakdown(df_geo) + '</div>')

    # B. Country drill-down
    s += ('<div class="subsection"><h3>B. Country Drill-Down (Top 10 by Volume)</h3>'
          + LEGEND + build_country_table(df_geo) + '</div>')

    # C. Recommendation profile
    s += (f'<div class="subsection"><h3>C. Recommendation Profile (AI Rows Only)</h3>'
          f'<p class="insight">AI-recommended rows: <strong>{fc(k["ai_count"])}</strong> '
          f'({fp(k["ai_pct"])} of all configs). '
          f'Compares what the model recommends vs what reps select when they deviate.</p>'
          + build_rec_overview(df_geo) + '</div>')

    # D. Coverage gaps
    s += ('<div class="subsection"><h3>D. Improvement Area 1 &mdash; Coverage Gaps (No Default)</h3>'
          '<p class="insight">Countries or config origins where the AI has no recommendation '
          'but service is still sold. Prime expansion targets &mdash; adding coverage here '
          'could directly lift attach rates.</p>'
          + build_coverage_gap(df_geo) + '</div>')

    # E. Low acceptance
    s += ('<div class="subsection"><h3>E. Improvement Area 2 &mdash; Low Acceptance Segments '
          '(High Change Rate)</h3>'
          '<p class="insight">Countries or config origins where reps frequently override '
          'the AI recommendation. High change rate signals a mismatch between the model\'s '
          'default and market preference &mdash; these need model retraining or data refresh.</p>'
          + build_low_acceptance(df_geo) + '</div>')

    # F. Attachment failure
    s += ('<div class="subsection"><h3>F. Improvement Area 3 &mdash; Attachment Failures '
          '(Shown but Not Sold)</h3>'
          '<p class="insight">Where the AI shows a recommendation but the rep sells no service. '
          'The model is present but not driving conversion &mdash; may need a stronger default '
          'PN, pricing signal, or rep coaching.</p>'
          + build_att_failure(df_geo) + '</div>')

    # G. Monthly trend
    s += ('<div class="subsection"><h3>G. Improvement Area 4 &mdash; Monthly Trend</h3>'
          '<p class="insight">Monthly acceptance, attach, and AI coverage rates from go-live. '
          'Rising acceptance signals the model is improving; a sustained downward trend '
          'warrants investigation of recent model changes or data drift.</p>'
          + LEGEND + build_trend(df_geo) + '</div>')

    s += '</div></div>'
    return s


# ── EXECUTIVE SUMMARY ──────────────────────────────────────────────────────────
def build_exec_summary(df):
    s = ('<div class="section" id="summary">'
         '<div class="section-header"><h2>Executive Summary &mdash; Global Overview</h2></div>'
         '<div class="section-body">'
         '<p class="insight">&#9432; Each GEO is filtered from its go-live date: '
         'EMEA from 2025-09-28, AP / LA / NA from 2025-11-28.</p>')

    # KPI cards
    s += '<div class="card-grid">'
    for geo in GEOS:
        start = GEO_START[geo]
        sub   = df[(df['geo'] == geo) & (df['_date'] >= start)]
        k     = compute_kpis(sub)
        acc   = k['acceptance_pct']
        col   = ('#2e7d32' if (isinstance(acc, float) and np.isnan(acc)) or acc >= 55
                 else '#f57f17' if acc >= 45 else '#c62828')
        s += (f'<div class="kpi-card">'
              f'<div class="geo-tag">{geo}</div>'
              f'<div class="label">Acceptance Rate</div>'
              f'<div class="big" style="color:{col}">{fp(acc)}</div>'
              f'<div class="sub">{fc(k["total"])} configs &nbsp;|&nbsp; '
              f'{fp(k["coverage_pct"])} coverage</div>'
              f'<div class="sub" style="margin-top:3px;color:#aaa">'
              f'from {start.strftime("%Y-%m-%d")}</div>'
              f'</div>')
    s += '</div>'

    # Cross-GEO comparison table
    s += ('<h3 style="font-size:14px;font-weight:600;color:#37474f;margin-bottom:10px;'
          'border-left:4px solid #42a5f5;padding-left:10px">Cross-GEO KPI Comparison</h3>'
          + LEGEND)
    s += ('<table><tr><th>GEO</th>'
          '<th style="text-align:right">From</th>'
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
        sub   = df[(df['geo'] == geo) & (df['_date'] >= start)]
        k     = compute_kpis(sub)
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
    nav_links = ''.join(f'<a href="#{g}">{g}</a>' for g in GEOS)

    navbar = (f'<nav class="navbar">'
              f'<span class="brand">Service Smart Recommendation &mdash; Operational KPI Report (Excel)</span>'
              f'<a href="#summary">Executive Summary</a>'
              f'{nav_links}'
              f'<span class="meta">Data: {period} &nbsp;|&nbsp; Generated: {generated}</span>'
              f'</nav>')

    print('Building Executive Summary...', flush=True)
    parts = [build_exec_summary(df)]
    print('Building GEO sections...', flush=True)
    for geo in GEOS:
        parts.append(build_geo_section(df, geo))

    return (f'<!DOCTYPE html>\n<html lang="en">\n<head>\n'
            f'<meta charset="UTF-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1.0">'
            f'<title>Service Smart — Operational KPI Report (Excel)</title>\n'
            f'{STYLE}\n</head>\n<body>\n'
            f'{navbar}\n<div class="page">\n'
            + '\n'.join(parts)
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
