"""
Service Smart Recommendation — Combined Analysis
Period : 2025-11-28  to  2026-04-01
Sources: Ai_Report_20250815~20260306.xlsx  (rows up to 2026-03-16)
         Ai_Report_2026-04-01(3.17-4.01).xlsx (rows 2026-03-17 to 2026-04-01)

Metrics (same definitions as validate.py):
  Total Config      = all rows in scope
  Defaults          = defaultServicePn1 is not blank
  Default and sold  = Defaults AND selectedServicePn1 is not blank
  Accepted          = Defaults AND selectedServicePn1 == defaultServicePn1
  Changed           = Default and sold  -  Accepted
  No default        = defaultServicePn1 is blank
  No default sold   = No default AND selectedServicePn1 not blank AND selectedFrom not blank

Rates:
  Defaults%          = Defaults        / Total Config
  Default and sold%  = Default and sold / Total Config
  Accepted%          = Accepted         / Defaults
  Changed%           = Changed          / Defaults
  No def but sold%   = No def but sold  / No default
"""

import pandas as pd
import os, warnings
from datetime import date

warnings.filterwarnings('ignore')

FILE_OLD = 'Ai_Report_20250815~20260306.xlsx'
FILE_NEW = 'Ai_Report_2026-04-01(3.17-4.01).xlsx'
OUT      = 'validation_output/combined_analysis_1128_0401.txt'
os.makedirs('validation_output', exist_ok=True)

ANALYSIS_START = date(2025, 11, 28)
ANALYSIS_END   = date(2026,  4,  1)
OLD_CUTOFF     = date(2026,  3, 16)   # old file: up to and including this date
NEW_START      = date(2026,  3, 17)   # new file: from this date

KEEP_COLS = ['configuredFrom', 'geo', 'defaultServicePn1',
             'selectedServicePn1', 'selectedFrom']

# ── 1. Load old file ──────────────────────────────────────────────────────────
print(f"Loading {FILE_OLD} ...")
df_old = pd.read_excel(FILE_OLD, sheet_name='Ai-Report', engine='openpyxl',
                        keep_default_na=False)
df_old.columns = df_old.columns.str.strip()
df_old['_date'] = pd.to_datetime(df_old['create date'], errors='coerce').dt.date
mask_old = (df_old['_date'] >= ANALYSIS_START) & (df_old['_date'] <= OLD_CUTOFF)
df_old = df_old.loc[mask_old, KEEP_COLS + ['_date']].copy()
print(f"  Old file rows in scope (11-28 to 03-16): {len(df_old):,}")

# ── 2. Load new file ──────────────────────────────────────────────────────────
print(f"Loading {FILE_NEW} ...")
df_new = pd.read_excel(FILE_NEW, sheet_name='Ai-Report', engine='openpyxl',
                        keep_default_na=False)
df_new.columns = df_new.columns.str.strip()
df_new['_date'] = pd.to_datetime(df_new['createdDate'], utc=True,
                                  errors='coerce').dt.date
mask_new = (df_new['_date'] >= NEW_START) & (df_new['_date'] <= ANALYSIS_END)
df_new = df_new.loc[mask_new, KEEP_COLS + ['_date']].copy()
print(f"  New file rows in scope (03-17 to 04-01): {len(df_new):,}")

# ── 3. Combine ────────────────────────────────────────────────────────────────
df = pd.concat([df_old, df_new], ignore_index=True)
print(f"  Combined total rows               : {len(df):,}")
print(f"  Combined date range               : {df['_date'].min()} to {df['_date'].max()}")
print(f"  Geo breakdown: {df['geo'].value_counts().to_dict()}")

# ── 4. Derive flags ───────────────────────────────────────────────────────────
sp1 = df['selectedServicePn1'].astype(str).str.strip()
dp1 = df['defaultServicePn1'].astype(str).str.strip()
sf  = df['selectedFrom'].astype(str).str.strip()

df['has_default'] = dp1 != ''
df['has_sold']    = sp1 != ''
df['is_accepted'] = df['has_default'] & (sp1 == dp1)
df['has_sf']      = sf  != ''

# ── 5. Metric computation ─────────────────────────────────────────────────────
METRICS = ['Total Config', 'Defaults', 'Default and sold',
           'Accepted', 'Changed', 'No default', 'No default sold']

def compute(subset):
    has_d      = subset['has_default']
    defaults_  = has_d.sum()
    def_sold   = (has_d & subset['has_sold']).sum()
    accepted   = subset['is_accepted'].sum()
    no_default = (~has_d).sum()
    no_def_sold = (~has_d & subset['has_sold'] & subset['has_sf']).sum()
    return {
        'Total Config':      len(subset),
        'Defaults':          int(defaults_),
        'Default and sold':  int(def_sold),
        'Accepted':          int(accepted),
        'Changed':           int(def_sold - accepted),
        'No default':        int(no_default),
        'No default sold':   int(no_def_sold),
    }

def pct(num, den):
    return f"{num / den * 100:.1f}%" if den else "—"

GEO_MAP = {'WW': None, 'AP': 'AP', 'EMEA': 'EMEA', 'LA': 'LA', 'NA': 'NA'}
CF_GROUPS = {
    'Config from all':          None,
    'Config from new + copied': ['New CTO', 'Copied CTO'],
    'Config from new':          ['New CTO'],
}

# ── 6. Build report ───────────────────────────────────────────────────────────
lines = []
def ln(s=''):
    lines.append(s)

ln("SERVICE SMART RECOMMENDATION — COMBINED ANALYSIS")
ln(f"Period  : {ANALYSIS_START}  to  {ANALYSIS_END}")
ln(f"Sources : {FILE_OLD}  (rows up to 2026-03-16)")
ln(f"          {FILE_NEW}  (rows 2026-03-17 to 2026-04-01)")
ln(f"Total rows in scope : {len(df):,}")
ln(f"Geo breakdown       : { {g: (df['geo']==g).sum() for g in ['EMEA','NA','AP','LA']} }")
ln()

SEP  = "=" * 80
SEP2 = "-" * 80

def fmt_row(label, m, rate_den_tc, rate_den_d, rate_den_nd):
    count = m[label]
    if label == 'Total Config':
        r = "—"
    elif label in ('Defaults', 'Default and sold'):
        r = pct(count, rate_den_tc)
    elif label in ('Accepted', 'Changed'):
        r = pct(count, rate_den_d)
    elif label == 'No default':
        r = "—"
    elif label == 'No default sold':
        r = pct(count, rate_den_nd)
    else:
        r = "—"
    return f"  {label:<22} {count:>10,}   {r:>7}"

HDR = f"  {'Metric':<22} {'Count':>10}   {'Rate':>7}"

for geo_label, geo_code in GEO_MAP.items():
    ln(SEP)
    ln(f"  GEO: {geo_label}")
    ln(SEP)

    df_geo = df if geo_code is None else df[df['geo'] == geo_code]

    for cf_label, cf_vals in CF_GROUPS.items():
        df_sub = df_geo if cf_vals is None else df_geo[df_geo['configuredFrom'].isin(cf_vals)]
        m = compute(df_sub)
        tc  = m['Total Config'] or 1
        d   = m['Defaults']     or 1
        nd  = m['No default']   or 1

        ln()
        ln(f"  {cf_label}   (n = {m['Total Config']:,})")
        ln(SEP2)
        ln(HDR)
        ln("  " + "-" * 44)
        for metric in METRICS:
            ln(fmt_row(metric, m, tc, d, nd))
        ln()

ln(SEP)
ln("  RATE DEFINITIONS")
ln(SEP)
ln("  Defaults%         = Defaults / Total Config")
ln("  Default and sold% = Default and sold / Total Config")
ln("  Accepted%         = Accepted / Defaults")
ln("  Changed%          = Changed  / Defaults")
ln("  No default sold%  = No default sold / No default")
ln()
ln("  Accepted  : system showed a default recommendation AND customer kept it")
ln("              (selectedServicePn1 == defaultServicePn1)")
ln("  Changed   : system showed a default recommendation AND customer picked")
ln("              a different service (sold but not the exact default PN)")

report = "\n".join(lines)
print()
print(report)
with open(OUT, 'w', encoding='utf-8') as f:
    f.write(report)
print(f"\n[Saved to {OUT}]")
