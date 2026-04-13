"""
Generate sample_stage4_output.csv — simulated Stage 4 export for Stage 5 import.

Headers match Stage 4's exportCSV() exactly:
  Part Number, Tier, Base Warranty, Upgrade, Delivery Type, Upgrade Years,
  ADP, KYD, SBTY, TI CRU, Premier, Upgrade From Type, Upgrade From Term,
  Region, Sales Cost, Channel Price, Actual List Price,
  Computed B2C List Price, Computed B2B Floor

Rows are designed to exercise all combinations:
  - All 5 tiers (TP Tablet/Premium/Classic/Edge/Education)
  - Years 1-5
  - Delivery types: Onsite, Express Depot, Depot
  - BW groups via upgrade_from: fresh (→d1c), from 3Y CCI (→d3c), from 3Y Onsite (→d3o), from 4Y CCI (→d4c)
  - Regions from all default geo groups (CENTRAL, SOUTH, UKIR, BENELUX, EET, NA, APJ)
  - Various add-on combinations (ADP, KYD, SBTY, TI CRU, Premier)

Channel Price / Actual List Price left blank — Stage 5 calculates these.
Sales Cost = realistic values at roughly 40-55% of expected PFV.
"""

import csv, io

HEADERS = [
    'Part Number', 'Tier', 'Base Warranty', 'Upgrade', 'Delivery Type',
    'Upgrade Years', 'ADP', 'KYD', 'SBTY', 'TI CRU', 'Premier',
    'Upgrade From Type', 'Upgrade From Term',
    'Region', 'Sales Cost', 'Channel Price', 'Actual List Price',
    'Computed B2C List Price', 'Computed B2B Floor',
]

# ---------------------------------------------------------------------------
# Row definitions
# Each tuple: (part#, tier, base_warranty, upgrade_desc, delivery, upg_years,
#              adp, kyd, sbty, ticru, premier, upg_from_type, upg_from_term,
#              region, sales_cost)
# ---------------------------------------------------------------------------
ROWS = [
    # ── TP PREMIUM · Onsite · Fresh (d1c_onsite) ──────────────────────────
    # PFV d1c_onsite: yr1=25, yr2=80, yr3=150, yr4=220, yr5=285
    ('5WS1P1DE01','TP Premium','1Y Base','1Y Onsite NBD','Onsite', 1, 'N','N','N','N','N','','',        'DE', 13),
    ('5WS1P2FR01','TP Premium','1Y Base','2Y Onsite NBD','Onsite', 2, 'N','N','N','N','N','','',        'FR', 40),
    ('5WS1P3GB01','TP Premium','1Y Base','3Y Onsite NBD','Onsite', 3, 'N','N','N','N','N','','',        'GB', 78),
    ('5WS1P4US01','TP Premium','1Y Base','4Y Onsite NBD','Onsite', 4, 'N','N','N','N','N','','',        'US',115),
    ('5WS1P5AU01','TP Premium','1Y Base','5Y Onsite NBD','Onsite', 5, 'N','N','N','N','N','','',        'AU',148),

    # ── TP PREMIUM · Onsite · Upsell from 3Y CCI (d3c_onsite) ────────────
    # PFV d3c_onsite: yr3=60, yr4=130, yr5=230
    ('5WS1P3DE02','TP Premium','3Y CCI','3Y→3Y Onsite', 'Onsite', 3, 'N','N','N','N','N','CCI Depot','3', 'DE', 30),
    ('5WS1P4FR02','TP Premium','3Y CCI','3Y→4Y Onsite', 'Onsite', 4, 'N','N','N','N','N','CCI Depot','3', 'FR', 65),
    ('5WS1P5GB02','TP Premium','3Y CCI','3Y→5Y Onsite', 'Onsite', 5, 'N','N','N','N','N','CCI Depot','3', 'GB',118),

    # ── TP PREMIUM · Onsite · Upsell from 3Y Onsite (d3o_onsite) ─────────
    # PFV d3o_onsite: yr4=80, yr5=165
    ('5WS1P4DE03','TP Premium','3Y Onsite','3Y→4Y Onsite','Onsite',4, 'N','N','N','N','N','Onsite','3',   'DE', 40),
    ('5WS1P5FR03','TP Premium','3Y Onsite','3Y→5Y Onsite','Onsite',5, 'N','N','N','N','N','Onsite','3',   'FR', 82),

    # ── TP PREMIUM · Onsite · Upsell from 4Y CCI (d4c_onsite) ───────────
    # PFV d4c_onsite: yr4=70, yr5=160
    ('5WS1P4BE04','TP Premium','4Y CCI','4Y→4Y Onsite', 'Onsite', 4, 'N','N','N','N','N','CCI Depot','4', 'BE', 35),
    ('5WS1P5NL04','TP Premium','4Y CCI','4Y→5Y Onsite', 'Onsite', 5, 'N','N','N','N','N','CCI Depot','4', 'NL', 78),

    # ── TP PREMIUM · Onsite + ADP add-on ─────────────────────────────────
    # PFV d1c_onsite yr3=150 + ADP yr3=90 = 240 expected adj PFV
    ('5WS1P3IT05','TP Premium','1Y Base','3Y Onsite+ADP','Onsite', 3, 'Y','N','N','N','N','','',          'IT', 88),
    # PFV d1c_onsite yr2=80 + KYD yr2=15 = 95
    ('5WS1P2ES05','TP Premium','1Y Base','2Y Onsite+KYD','Onsite', 2, 'N','Y','N','N','N','','',          'ES', 38),
    # PFV d1c_onsite yr3=150 + Premier yr3=90
    ('5WS1P3RO05','TP Premium','1Y Base','3Y Onsite+Premier','Onsite',3,'N','N','N','N','Y','','',        'RO', 85),

    # ── TP CLASSIC · Onsite · Fresh (d1c_onsite) ─────────────────────────
    # PFV d1c_onsite: yr1=15, yr2=50, yr3=100, yr4=150, yr5=220
    ('5WS1C1DE01','TP Classic','1Y Base','1Y Onsite NBD','Onsite', 1, 'N','N','N','N','N','','',          'DE',  8),
    ('5WS1C2FR01','TP Classic','1Y Base','2Y Onsite NBD','Onsite', 2, 'N','N','N','N','N','','',          'FR', 27),
    ('5WS1C3GB01','TP Classic','1Y Base','3Y Onsite NBD','Onsite', 3, 'N','N','N','N','N','','',          'GB', 52),
    ('5WS1C4CA01','TP Classic','1Y Base','4Y Onsite NBD','Onsite', 4, 'N','N','N','N','N','','',          'CA', 80),
    ('5WS1C5AU01','TP Classic','1Y Base','5Y Onsite NBD','Onsite', 5, 'N','N','N','N','N','','',          'AU',115),

    # ── TP CLASSIC · Onsite · Upsell from 3Y Onsite (d3o_onsite) ─────────
    # PFV d3o_onsite: yr4=60, yr5=120
    ('5WS1C4DE02','TP Classic','3Y Onsite','3Y→4Y Onsite','Onsite',4, 'N','N','N','N','N','Onsite','3',   'DE', 30),
    ('5WS1C5FR02','TP Classic','3Y Onsite','3Y→5Y Onsite','Onsite',5, 'N','N','N','N','N','Onsite','3',   'FR', 60),

    # ── TP CLASSIC · Express Depot · Fresh (d1c_exp) ──────────────────────
    # PFV d1c_exp: yr1=10, yr2=40, yr3=80, yr4=140, yr5=210
    ('5WS1C2BE01','TP Classic','1Y Base','2Y Exp Depot', 'Express Depot',2,'N','N','N','N','N','','',     'BE', 20),
    ('5WS1C3US01','TP Classic','1Y Base','3Y Exp Depot', 'Express Depot',3,'N','N','N','N','N','','',     'US', 42),

    # ── TP EDGE · Depot · Fresh (d1c_depot) ──────────────────────────────
    # PFV d1c_depot: yr1=0, yr2=28, yr3=62, yr4=110, yr5=168
    ('5WS1E2DE01','TP Edge',   '1Y Base','2Y Depot NBD', 'Depot',  2, 'N','N','N','N','N','','',          'DE', 14),
    ('5WS1E3FR01','TP Edge',   '1Y Base','3Y Depot NBD', 'Depot',  3, 'N','N','N','N','N','','',          'FR', 32),
    ('5WS1E4GB01','TP Edge',   '1Y Base','4Y Depot NBD', 'Depot',  4, 'N','N','N','N','N','','',          'GB', 57),
    ('5WS1E5US01','TP Edge',   '1Y Base','5Y Depot NBD', 'Depot',  5, 'N','N','N','N','N','','',          'US', 88),

    # ── TP EDGE · Onsite · Fresh ──────────────────────────────────────────
    # PFV d1c_onsite: yr1=12, yr2=42, yr3=82, yr4=125, yr5=183
    ('5WS1E3SG01','TP Edge',   '1Y Base','3Y Onsite NBD','Onsite', 3, 'N','N','N','N','N','','',          'SG', 42),
    # with TI CRU add-on: PFV d1c_onsite yr3=82 + TI CRU yr3=28 = 110
    ('5WS1E3AT01','TP Edge',   '1Y Base','3Y Onsite+TICRU','Onsite',3,'N','N','N','Y','N','','',          'AT', 46),

    # ── TP TABLET · Express Depot · Fresh (d1c_exp) ───────────────────────
    # PFV d1c_exp: yr1=20, yr2=70, yr3=140, yr4=210, yr5=280
    ('5WS1T1DE01','TP Tablet', '1Y Base','1Y Exp Depot', 'Express Depot',1,'N','N','N','N','N','','',     'DE', 10),
    ('5WS1T2FR01','TP Tablet', '1Y Base','2Y Exp Depot', 'Express Depot',2,'N','N','N','N','N','','',     'FR', 36),
    ('5WS1T3GB01','TP Tablet', '1Y Base','3Y Exp Depot', 'Express Depot',3,'N','N','N','N','N','','',     'GB', 72),
    # with ADP: PFV d1c_exp yr2=70 + ADP yr2=70 = 140
    ('5WS1T2US01','TP Tablet', '1Y Base','2Y Exp Depot+ADP','Express Depot',2,'Y','N','N','N','N','','',  'US', 50),
    # with SBTY: PFV d1c_exp yr3=140 + SBTY yr3=25 = 165
    ('5WS1T3CA01','TP Tablet', '1Y Base','3Y Exp Depot+SBTY','Express Depot',3,'N','N','Y','N','N','','', 'CA', 68),

    # ── TP EDUCATION · Depot · Fresh (d1c_depot) ──────────────────────────
    # PFV d1c_depot: yr1=0, yr2=22, yr3=50, yr4=88, yr5=135
    ('5WS1D2DE01','TP Education','1Y Base','2Y Depot NBD','Depot',  2, 'N','N','N','N','N','','',          'DE', 11),
    ('5WS1D3FR01','TP Education','1Y Base','3Y Depot NBD','Depot',  3, 'N','N','N','N','N','','',          'FR', 25),
    ('5WS1D4IN01','TP Education','1Y Base','4Y Depot NBD','Depot',  4, 'N','N','N','N','N','','',          'IN', 46),
    ('5WS1D5JP01','TP Education','1Y Base','5Y Depot NBD','Depot',  5, 'N','N','N','N','N','','',          'JP', 70),
]

# ---------------------------------------------------------------------------
# Write CSV
# ---------------------------------------------------------------------------
out_path = r'C:\Users\Administrator\ClaudeProjects\GPS_Cost_Pricing_Workbench\stage5_browser\sample_stage4_output.csv'

with open(out_path, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f, quoting=csv.QUOTE_ALL)
    w.writerow(HEADERS)
    for r in ROWS:
        pn, tier, bw, upg, dt, yrs, adp, kyd, sbty, ticru, prem, uft, ufterm, region, sc = r
        w.writerow([pn, tier, bw, upg, dt, yrs, adp, kyd, sbty, ticru, prem, uft, ufterm,
                    region, sc, '', '', '', ''])

print(f'Saved: {out_path}')
print(f'Rows written: {len(ROWS)}')
print()
print('Coverage summary:')
tiers = {}
for r in ROWS:
    tiers[r[1]] = tiers.get(r[1], 0) + 1
for t, n in tiers.items():
    print(f'  {t}: {n} rows')
regions = set(r[13] for r in ROWS)
print(f'Regions: {sorted(regions)}')
bw_groups = set()
for r in ROWS:
    uft, ufterm = r[11], r[12]
    if not uft:
        bw_groups.add('d1c (fresh)')
    elif 'Onsite' in uft and ufterm == '3':
        bw_groups.add('d3o (from 3Y Onsite)')
    elif 'CCI' in uft and ufterm == '3':
        bw_groups.add('d3c (from 3Y CCI)')
    elif ufterm == '4':
        bw_groups.add('d4c (from 4Y CCI)')
print(f'BW groups: {sorted(bw_groups)}')
