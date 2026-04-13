"""
GPS Cost Pricing Workbench — Sample Data Generator
Generates a single consistent dataset for demoing Stages 3 → 4 → 5 → 6.

All files share the same 60 SKUs: 5 tiers × 4 regions × 3 terms, Onsite delivery.

Output files (all in this folder):
  Stage3_SKU_Input.csv        → import into Stage 3
  Stage4_Input.xlsx           → import into Stage 4  (Stage 3 "Send to Stage 4" output)
  Stage5_SKU_Input.csv        → import into Stage 5  (SKU data with sales_cost)
  Stage5_PFV_Input.csv        → import into Stage 5  (PFV benchmark)
  Stage6_Standalone_Input.csv → import into Stage 6  (list prices, for independent demo)
"""

import csv, math, os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

OUT = os.path.dirname(os.path.abspath(__file__))

# ── Master dimensions ──────────────────────────────────────────────────────────

TIERS = [
    # (code, display_name, stage3_tier, stage3_sub_tier, base_psc_1yr_DE)
    ('ED', 'TP Education', 'TP Education', 'Standard',  28),
    ('TB', 'TP Tablet',    'TP Tablet',    'Standard',  38),
    ('CL', 'TP Classic',   'TP Classic',   'Standard',  52),
    ('PM', 'TP Premium',   'TP Premium',   'High-End',  72),
    ('EG', 'TP Edge',      'TP Edge',      'High-End',  92),
]

REGIONS = [
    # (code, geo, regional_factor)
    ('DE', 'EMEA', 1.000),
    ('FR', 'EMEA', 1.050),
    ('GB', 'EMEA', 1.140),
    ('US', 'NA',   0.930),
]

TERMS = [
    # (years, term_factor, months_label)
    (1, 1.000, '12'),
    (3, 2.375, '36'),
    (5, 3.571, '60'),
]

DELIVERY    = 'Onsite'
UPLIFT_PCT  = 0.20     # Stage 3 uplift: 20%
GP_PCT      = 0.30     # Stage 5 GP%: 30%  →  List Price = Sales Cost / (1 - 0.30)
PFV_FACTOR  = 1.55     # PFV = Sales Cost(DE) × 1.55 per tier/term

# OH IDs for Stage 3
OH_MAP = {'EMEA': ('OH-001', 'Lenovo EMEA Support'), 'NA': ('OH-003', 'Lenovo NA Support')}

def r(x):
    """Round to nearest integer."""
    return int(math.floor(x + 0.5))

# ── Build master table ─────────────────────────────────────────────────────────
# Each row: part_number, tier_code, tier_name, stage3_tier, stage3_sub, region,
#           geo, years, psc, sales_cost, pfv, list_price

rows = []
seq = 1
for tc, tn, s3t, s3s, base in TIERS:
    for rc, geo, rfac in REGIONS:
        for yrs, tfac, months in TERMS:
            psc   = base * rfac * tfac
            sc    = psc * (1 + UPLIFT_PCT)
            pn    = f'5WS2{tc}{yrs}{rc}{seq:03d}'
            seq  += 1
            rows.append({
                'part_number': pn,
                'tier_code':   tc,
                'tier':        tn,
                'stage3_tier': s3t,
                'stage3_sub':  s3s,
                'region':      rc,
                'geo':         geo,
                'years':       yrs,
                'months':      months,
                'psc':         r(psc),
                'sales_cost':  r(sc),
            })

# Compute PFV per (tier, years) using DE as reference
pfv_map = {}
for tc, tn, _, _, base in TIERS:
    for yrs, tfac, _ in TERMS:
        sc_de = base * 1.000 * tfac * (1 + UPLIFT_PCT)
        pfv_map[(tn, yrs)] = r(sc_de * PFV_FACTOR)

for row in rows:
    row['pfv']        = pfv_map[(row['tier'], row['years'])]
    row['list_price'] = r(row['sales_cost'] / (1 - GP_PCT))


# ═══════════════════════════════════════════════════════════════════════════════
# FILE 1: Stage3_SKU_Input.csv
# ═══════════════════════════════════════════════════════════════════════════════

S3_HEADERS = [
    'Service PN', 'Service PN Short Description', 'Service PN Sales& Marketing Description',
    'OH ID', 'OH Name', 'Type of Service', 'Sub-Type of Service', 'Offering Type',
    'Standard Cost ( Base Cost )', 'Currency', 'GEO', 'Country',
    'Service Tier', 'Sub Service Tier', 'Compatible MT', 'SDF Code',
    'SDF Code Short Description', 'SDF Code Long Description',
    'Service Term', 'Unit', 'Service Availability Time', 'Service Response Time',
    'Service Delivery Type', 'Upgrade From Type', 'Upgrade From Term',
    'Included Premier Service', 'Premier Service Type',
    'Included Protection Service', 'Included KYD Service',
    'Included SBTY Service', 'Included ISE Service', 'Included TI CRU Service',
]

tier_short = {'TP Education':'EDU','TP Tablet':'TAB','TP Classic':'CLS',
               'TP Premium':'PRM','TP Edge':'EDG'}
deliv_code = {'Onsite':'ON-SITE'}

with open(os.path.join(OUT, 'Stage3_SKU_Input.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=S3_HEADERS)
    w.writeheader()
    for row in rows:
        ts  = tier_short[row['tier']]
        oh_id, oh_name = OH_MAP[row['geo']]
        sdf = f'SDF-{ts}-{row["years"]}Y'
        w.writerow({
            'Service PN':                          row['part_number'],
            'Service PN Short Description':        f'{row["years"]}Y ONS NBD {ts} {row["region"]}',
            'Service PN Sales& Marketing Description': f'{row["years"]} Year Onsite NBD — {row["tier"]} {row["region"]}',
            'OH ID':                               oh_id,
            'OH Name':                             oh_name,
            'Type of Service':                     'Support Services',
            'Sub-Type of Service':                 'Hardware Support',
            'Offering Type':                       'Hardware Support',
            'Standard Cost ( Base Cost )':         row['psc'],
            'Currency':                            'USD',
            'GEO':                                 row['geo'],
            'Country':                             row['region'],
            'Service Tier':                        row['stage3_tier'],
            'Sub Service Tier':                    row['stage3_sub'],
            'Compatible MT':                       '20B7',
            'SDF Code':                            sdf,
            'SDF Code Short Description':          f'{ts} {row["years"]}Y Onsite',
            'SDF Code Long Description':           f'{row["tier"]} {row["years"]} Year Onsite NBD',
            'Service Term':                        row['months'],
            'Unit':                                'Each',
            'Service Availability Time':           '9x5',
            'Service Response Time':               'NBD',
            'Service Delivery Type':               deliv_code[DELIVERY],
            'Upgrade From Type':                   '',
            'Upgrade From Term':                   '',
            'Included Premier Service':            'N',
            'Premier Service Type':                '',
            'Included Protection Service':         'N',
            'Included KYD Service':                'N',
            'Included SBTY Service':               'N',
            'Included ISE Service':                'N',
            'Included TI CRU Service':             'N',
        })

print('Stage3_SKU_Input.csv written')


# ═══════════════════════════════════════════════════════════════════════════════
# FILE 2: Stage4_Input.xlsx  (matrix format matching Stage 3 "Send to Stage 4")
# ═══════════════════════════════════════════════════════════════════════════════

# Build pivot: per part_number, the sales_cost by region
# Also need: Tier, Base Warranty, Upgrade, Type (descriptive cols)
# Stage 4 expects: Part# | Tier | Base Warranty | Upgrade | Type |
#                  [Region_Cost | Region_C-Price | Region_L-Price] per region

region_order = [r[0] for r in REGIONS]

wb4 = openpyxl.Workbook()
ws4 = wb4.active
ws4.title = 'Pricing'

# ── Styles ──
hdr_font   = Font(bold=True, color='FFFFFF', size=10)
hdr_fill   = PatternFill('solid', fgColor='1A1A1A')
geo_fills  = {
    'DE': PatternFill('solid', fgColor='2E3F5C'),
    'FR': PatternFill('solid', fgColor='1A4A2E'),
    'GB': PatternFill('solid', fgColor='4A1A2E'),
    'US': PatternFill('solid', fgColor='4A3A1A'),
}
geo_font   = Font(bold=True, color='FFFFFF', size=10)
thin       = Side(style='thin', color='D9D8D6')
bdr        = Border(left=thin, right=thin, top=thin, bottom=thin)

# Row 1: geo group headers
desc_cols = 5
ws4.cell(1, 1).value = 'Part#'
ws4.cell(1, 2).value = 'Tier'
ws4.cell(1, 3).value = 'Base Warranty'
ws4.cell(1, 4).value = 'Upgrade'
ws4.cell(1, 5).value = 'Type'
for i in range(1, 6):
    c = ws4.cell(1, i)
    c.font = hdr_font; c.fill = hdr_fill; c.alignment = Alignment(horizontal='center')

for ri, rc in enumerate(region_order):
    col_start = desc_cols + 1 + ri * 3
    ws4.merge_cells(start_row=1, start_column=col_start,
                    end_row=1,   end_column=col_start + 2)
    c = ws4.cell(1, col_start)
    c.value = rc
    c.font = geo_font; c.fill = geo_fills[rc]
    c.alignment = Alignment(horizontal='center')

# Row 2: sub-headers
for i, h in enumerate(['Part#','Tier','Base Warranty','Upgrade','Type'], 1):
    c = ws4.cell(2, i)
    c.value = h; c.font = hdr_font; c.fill = hdr_fill
    c.alignment = Alignment(horizontal='center')

for ri, rc in enumerate(region_order):
    col_start = desc_cols + 1 + ri * 3
    for j, sub in enumerate(['Cost', 'C-Price', 'L-Price']):
        c = ws4.cell(2, col_start + j)
        c.value = sub; c.font = geo_font; c.fill = geo_fills[rc]
        c.alignment = Alignment(horizontal='center')

# Data rows: one row per unique (part_number, tier, years) — pivot across regions
# Each part_number exists for one specific region in our dataset, so rows are per-SKU
# But Stage 4 expects one row per (tier, term) combination with all geo costs together.
# Group by (tier, years, delivery_type) and put each region's cost in its column.

from collections import defaultdict
groups = defaultdict(dict)  # (tier, base_warranty, upgrade_desc, type_) -> {region: sales_cost}

upgrade_label = {1: '1Y Onsite NBD', 3: '3Y Onsite NBD', 5: '5Y Onsite NBD'}
base_label    = {1: '1Y Base',        3: '3Y Base',        5: '5Y Base'}

# Use a representative part number (DE version) per tier/term
rep_pn = {}
for row in rows:
    key = (row['tier'], row['years'])
    if row['region'] == 'DE':
        rep_pn[key] = row['part_number']

for row in rows:
    key = (row['tier'], row['years'])
    pn  = rep_pn.get(key, row['part_number'])
    grp_key = (pn, row['tier'], '1Y Base', upgrade_label[row['years']], 'Support Services')
    groups[grp_key][row['region']] = row['sales_cost']

data_row = 3
for (pn, tier, base_w, upgrade, svc_type), region_costs in sorted(
        groups.items(), key=lambda x: (x[0][1], x[0][3])):
    ws4.cell(data_row, 1).value = pn
    ws4.cell(data_row, 2).value = tier
    ws4.cell(data_row, 3).value = base_w
    ws4.cell(data_row, 4).value = upgrade
    ws4.cell(data_row, 5).value = svc_type
    for ri, rc in enumerate(region_order):
        col_start = desc_cols + 1 + ri * 3
        ws4.cell(data_row, col_start).value = region_costs.get(rc, None)
    data_row += 1

# Column widths
col_widths = [18, 14, 14, 20, 18] + [10, 10, 10] * len(region_order)
for i, w in enumerate(col_widths, 1):
    ws4.column_dimensions[get_column_letter(i)].width = w

wb4.save(os.path.join(OUT, 'Stage4_Input.xlsx'))
print('Stage4_Input.xlsx written')


# ═══════════════════════════════════════════════════════════════════════════════
# FILE 3: Stage5_SKU_Input.csv
# ═══════════════════════════════════════════════════════════════════════════════

S5_HEADERS = ['part_number', 'tier', 'upgrade_years', 'delivery_type', 'region', 'sales_cost']

with open(os.path.join(OUT, 'Stage5_SKU_Input.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=S5_HEADERS)
    w.writeheader()
    for row in rows:
        w.writerow({
            'part_number':   row['part_number'],
            'tier':          row['tier'],
            'upgrade_years': row['years'],
            'delivery_type': DELIVERY,
            'region':        row['region'],
            'sales_cost':    row['sales_cost'],
        })

print('Stage5_SKU_Input.csv written')


# ═══════════════════════════════════════════════════════════════════════════════
# FILE 4: Stage5_PFV_Input.csv
# ═══════════════════════════════════════════════════════════════════════════════

PFV_HEADERS = ['tier', 'upgrade_years', 'delivery_type', 'pfv_value']

seen_pfv = set()
with open(os.path.join(OUT, 'Stage5_PFV_Input.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=PFV_HEADERS)
    w.writeheader()
    for row in rows:
        key = (row['tier'], row['years'])
        if key not in seen_pfv:
            seen_pfv.add(key)
            w.writerow({
                'tier':          row['tier'],
                'upgrade_years': row['years'],
                'delivery_type': DELIVERY,
                'pfv_value':     row['pfv'],
            })

print('Stage5_PFV_Input.csv written')


# ═══════════════════════════════════════════════════════════════════════════════
# FILE 5: Stage6_Standalone_Input.csv  (for independent Stage 6 demo)
# ═══════════════════════════════════════════════════════════════════════════════

S6_HEADERS = ['part_number', 'tier', 'upgrade_years', 'delivery_type', 'region', 'list_price_calc']

with open(os.path.join(OUT, 'Stage6_Standalone_Input.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=S6_HEADERS)
    w.writeheader()
    for row in rows:
        w.writerow({
            'part_number':    row['part_number'],
            'tier':           row['tier'],
            'upgrade_years':  row['years'],
            'delivery_type':  DELIVERY,
            'region':         row['region'],
            'list_price_calc': row['list_price'],
        })

print('Stage6_Standalone_Input.csv written')


# ═══════════════════════════════════════════════════════════════════════════════
# VERIFICATION REPORT
# ═══════════════════════════════════════════════════════════════════════════════

print()
print('=== VERIFICATION ===')
print(f'Total SKUs: {len(rows)}  ({len(TIERS)} tiers × {len(REGIONS)} regions × {len(TERMS)} terms)')
print()

# L1 monotonicity check (DE, Onsite, per term)
print('L1 Monotonicity — tier order (DE, Onsite):')
for yrs, _, _ in TERMS:
    vals = []
    for tc, tn, _, _, _ in TIERS:
        r2 = next(x for x in rows if x['tier'] == tn and x['region'] == 'DE' and x['years'] == yrs)
        vals.append((tn, r2['list_price']))
    ok = all(vals[i][1] <= vals[i+1][1] for i in range(len(vals)-1))
    print(f'  {yrs}yr: {" < ".join(f"{t}={v}" for t,v in vals)} {"OK" if ok else "FAIL"}')

print()
# L2 ratio check
print('L2 Ratio Bands — 3yr/1yr (floor 1.8, ceiling 2.8):')
for tc, tn, _, _, _ in TIERS:
    for rc, _, _ in REGIONS:
        r1 = next(x for x in rows if x['tier'] == tn and x['region'] == rc and x['years'] == 1)
        r3 = next(x for x in rows if x['tier'] == tn and x['region'] == rc and x['years'] == 3)
        ratio = r3['list_price'] / r1['list_price']
        ok = 1.8 <= ratio <= 2.8
        print(f'  {tn} {rc}: {ratio:.2f} {"OK" if ok else "FAIL"}')

print()
# L3 cross-geo check (20% threshold)
print('L3 Cross-Geo — max deviation from mean (<20%):')
for tc, tn, _, _, _ in TIERS:
    for yrs, _, _ in TERMS:
        prices = []
        for rc, _, _ in REGIONS:
            r2 = next(x for x in rows if x['tier'] == tn and x['region'] == rc and x['years'] == yrs)
            prices.append(r2['list_price'])
        mean   = sum(prices) / len(prices)
        maxdev = max(abs(p - mean) / mean for p in prices)
        ok = maxdev < 0.20
        print(f'  {tn} {yrs}yr: max_dev={maxdev*100:.1f}% {"OK" if ok else "FAIL"}')

print()
print('PFV values (DE reference):')
for tn, yrs in sorted(pfv_map.keys(), key=lambda x:(x[0], x[1])):
    print(f'  {tn} {yrs}yr: {pfv_map[(tn, yrs)]}')
