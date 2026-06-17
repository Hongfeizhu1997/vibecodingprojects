"""
Service Smart Recommendation — Validation Script
Validates figures in analysis sheets (GEO 11.28-03.06 and GEO 08.15-03.06)
against raw Ai-Report data.

Metric definitions derived from raw data:
  Total Config      = all rows (filtered by period + geo + configuredFrom)
  Defaults          = rows where aiRecommendations is not empty ('[]' or null)
  Default and sold  = Defaults AND selectedServicePn1 is not null
  Accepted          = Defaults AND selectedFrom contains '(Default)'
  Changed           = Defaults AND selectedServicePn1 not null AND selectedFrom does NOT contain '(Default)'
  No default        = rows where aiRecommendations is empty/null
  No default sold   = No default AND selectedServicePn1 is not null
"""

import pandas as pd
from datetime import date
import os
import warnings
warnings.filterwarnings('ignore')

FILE = "Ai_Report_20250815~20260306.xlsx"
OUT  = "validation_output"
os.makedirs(OUT, exist_ok=True)

# ── 1. Load raw data ─────────────────────────────────────────────────────────
print("Loading raw data (268k rows)...")
df = pd.read_excel(FILE, sheet_name='Ai-Report', engine='openpyxl', keep_default_na=False)
df.columns = df.columns.str.strip()

# Normalise date column
df['create date'] = pd.to_datetime(df['create date'], errors='coerce').dt.date
print(f"  Loaded {len(df):,} rows. Date range: {df['create date'].min()} to {df['create date'].max()}")

# ── 2. Derive metric flags ────────────────────────────────────────────────────
# Validated definitions (confirmed against EMEA all Nov28-Mar6 stated figures):
#
#   Defaults        = defaultServicePn1 is not blank
#                     (system showed a default service recommendation)
#   Accepted        = has_default AND selectedServicePn1 == defaultServicePn1
#                     (customer kept the exact recommended service PN)
#   Default & sold  = has_default AND selectedServicePn1 is not blank
#   Changed         = Default & sold  minus  Accepted
#   No default      = defaultServicePn1 is blank
#   No def but sold = no_default AND selectedServicePn1 not blank AND selectedFrom not blank
#                     (25-row gap vs sheet when selectedFrom blank rows included;
#                      sheet appears to require a non-empty selectedFrom)

sp1 = df['selectedServicePn1'].astype(str).str.strip()
dp1 = df['defaultServicePn1'].astype(str).str.strip()
sf  = df['selectedFrom'].astype(str).str.strip()

df['has_default'] = dp1 != ''
df['has_sold']    = sp1 != ''
df['is_accepted'] = df['has_default'] & (sp1 == dp1)
df['has_sf']      = sf  != ''        # selectedFrom not blank

# ── 3. Helper: compute metrics for a filtered subset ─────────────────────────
def metrics(subset):
    total        = len(subset)
    has_d        = subset['has_default']
    defaults_    = has_d.sum()
    def_sold     = (has_d & subset['has_sold']).sum()
    accepted     = subset['is_accepted'].sum()
    changed      = def_sold - accepted
    no_default   = (~has_d).sum()
    # Sheet excludes rows where selectedFrom is blank for "No default but sold"
    no_def_sold  = (~has_d & subset['has_sold'] & subset['has_sf']).sum()
    return {
        'Total Config':          int(total),
        'Defaults':              int(defaults_),
        'Default and sold':      int(def_sold),
        'Accepted':              int(accepted),
        'Changed':               int(changed),
        'No default':            int(no_default),
        'No default but sold':   int(no_def_sold),
    }

# Rates row (denominators: Total Config for Defaults%; Defaults for the rest)
def rates(m):
    tc = m['Total Config'] or 1
    d  = m['Defaults']     or 1
    return {
        'Total Config':         None,
        'Defaults':             m['Defaults']            / tc,
        'Default and sold':     m['Default and sold']    / tc,
        'Accepted':             m['Accepted']            / d,
        'Changed':              m['Changed']             / d,
        'No default':           None,
        'No default but sold':  m['No default but sold'] / m['No default'] if m['No default'] else None,
    }

COLS = ['Total Config','Defaults','Default and sold','Accepted','Changed',
        'No default','No default but sold']

# configuredFrom groupings
CF_GROUPS = {
    'all':         None,                          # no filter
    'new+copied':  ['New CTO','Copied CTO'],
    'new':         ['New CTO'],
}

GEO_MAP = {
    'WW':   None,
    'AP':   'AP',
    'EMEA': 'EMEA',
    'LA':   'LA',
    'NA':   'NA',
}

# ── 4. Periods to validate ────────────────────────────────────────────────────
PERIODS = {
    'sheet_1128_0306': {
        'label':      '2025-11-28 to 2026-03-06',
        'start':      date(2025, 11, 28),
        'end':        date(2026,  3,  6),
        'sheet_name': 'GEO（11.28-03.06)',
    },
    'sheet_0815_0306': {
        'label':      '2025-08-15 to 2026-03-06',
        'start':      date(2025,  8, 15),
        'end':        date(2026,  3,  6),
        'sheet_name': 'GEO（08.15-03.06)',
    },
}

# ── 5. Load stated figures from analysis sheets ───────────────────────────────
import openpyxl

def parse_analysis_sheet(wb, sheet_name):
    """
    Returns a dict:  (geo, cf_group) -> {metric: value}
    cf_group: 'all', 'new+copied', 'new'

    Sheet layout (non-empty rows only):
      Row 0 : title
      Row 1 : GEO / WW
      Row 2 : column headers  (Total Config, Defaults, …)
      Row 3 : WW count data   <- values in cols 1-7
      Row 4 : WW rate data
      Row 5 : GEO / AP
      Row 6 : 'Config from all' + col headers combined
      Row 7 : AP-all count    <- values in cols 1-7
      Row 8 : AP-all rates
      Row 9 : 'Config from new + copied'
      Row 10: count
      Row 11: rates
      Row 12: 'Config from new'
      Row 13: count
      Row 14: rates
      … repeat for EMEA, LA, NA
    """
    ws = wb[sheet_name]
    rows = [r for r in ws.iter_rows(values_only=True) if any(v is not None for v in r)]

    def safe(v):
        try: return float(v) if v is not None else None
        except: return None

    result = {}
    current_geo = None
    cf_labels = {
        'Config from all':            'all',
        'Config from new + copied':   'new+copied',
        'Config from new':            'new',
    }

    i = 0
    while i < len(rows):
        row = rows[i]
        cell0 = str(row[0]).strip() if row[0] is not None else ''

        # ── GEO section header ──────────────────────────────────────────
        if cell0 == 'GEO' and row[1] is not None:
            current_geo = str(row[1]).strip()
            i += 1

            # WW has a separate column-header row, then count, then rate
            if current_geo == 'WW':
                i += 1  # skip column-header row
                if i < len(rows):
                    count_row = rows[i]; i += 1
                    rate_row  = rows[i] if i < len(rows) else (None,)*17
                    stated = [safe(count_row[j]) for j in range(1, 8)]
                    key = ('WW', 'all')
                    result[key] = dict(zip(COLS, stated))
                    i += 1
            continue

        # ── cf-group header (non-WW geos) ──────────────────────────────
        if cell0 in cf_labels:
            current_cf = cf_labels[cell0]
            # This row also carries the column sub-headers — skip it, next row = counts
            i += 1
            if i >= len(rows): break
            count_row = rows[i]; i += 1
            rate_row  = rows[i] if i < len(rows) else (None,)*17

            stated = [safe(count_row[j]) for j in range(1, 8)]
            key = (current_geo, current_cf)
            result[key] = dict(zip(COLS, stated))
            i += 1
            continue

        i += 1

    return result


wb_ref = openpyxl.load_workbook(FILE, data_only=True)

# ── 6. Run validation for each period ────────────────────────────────────────
all_results = []   # flat list of comparison rows for CSV output

for period_key, period in PERIODS.items():
    print(f"\n{'='*70}")
    print(f"VALIDATING: {period['label']}")
    print(f"{'='*70}")

    # Filter by date
    mask_date = (df['create date'] >= period['start']) & (df['create date'] <= period['end'])
    df_period = df[mask_date].copy()
    print(f"  Rows in period: {len(df_period):,}")

    # Parse stated figures from sheet
    stated_all = parse_analysis_sheet(wb_ref, period['sheet_name'])

    for geo_label, geo_code in GEO_MAP.items():
        # Geo filter
        if geo_code is None:
            df_geo = df_period
        else:
            df_geo = df_period[df_period['geo'] == geo_code]

        for cf_label, cf_vals in CF_GROUPS.items():
            if cf_vals is None:
                df_sub = df_geo
            else:
                df_sub = df_geo[df_geo['configuredFrom'].isin(cf_vals)]

            computed = metrics(df_sub)
            stated   = stated_all.get((geo_label, cf_label), {})

            if not stated:
                continue

            print(f"\n  GEO={geo_label}  configuredFrom={cf_label}  (n={len(df_sub):,})")
            print(f"  {'Metric':<22} {'Stated':>10} {'Computed':>10} {'Diff':>8}  {'Status'}")
            print(f"  {'-'*65}")

            for col in COLS:
                s = stated.get(col)
                c = computed.get(col)
                if s is None or c is None:
                    status = 'SKIP'
                    diff   = '-'
                else:
                    s = int(round(s))
                    diff_val = c - s
                    pct = abs(diff_val / s * 100) if s else 0
                    status = 'MATCH' if abs(diff_val) == 0 else (
                             'CLOSE (<1%)' if pct < 1 else
                             f'DISCREPANCY ({pct:.1f}%)')
                    diff = f'{diff_val:+,}'

                print(f"  {col:<22} {str(s) if s is not None else 'N/A':>10} {str(c):>10} {diff:>8}  {status}")

                all_results.append({
                    'Period':          period['label'],
                    'GEO':             geo_label,
                    'CF_Group':        cf_label,
                    'Metric':          col,
                    'Stated':          s if s is not None else '',
                    'Computed':        c,
                    'Difference':      (c - int(round(s))) if s is not None else '',
                    'Status':          status if s is not None else 'SKIP',
                })

# ── 7. Write CSV report ───────────────────────────────────────────────────────
out_path = os.path.join(OUT, 'validation_report.csv')
import csv
with open(out_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['Period','GEO','CF_Group','Metric',
                                           'Stated','Computed','Difference','Status'])
    writer.writeheader()
    writer.writerows(all_results)

print(f"\n\n{'='*70}")
print("SUMMARY")
print(f"{'='*70}")
statuses = [r['Status'] for r in all_results if r['Status'] != 'SKIP']
matches  = sum(1 for s in statuses if 'MATCH' in s)
close    = sum(1 for s in statuses if 'CLOSE' in s)
disc     = sum(1 for s in statuses if 'DISCREPANCY' in s)
print(f"  Total checks : {len(statuses)}")
print(f"  MATCH        : {matches}")
print(f"  CLOSE (~1%)  : {close}")
print(f"  DISCREPANCY  : {disc}")
print(f"\nReport written to: {out_path}")
