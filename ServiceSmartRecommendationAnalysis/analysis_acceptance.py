"""
Acceptance Rate & Coverage Analysis
- Config level  : each row/line_item is one observation
- Contract level: each unique contract_number is one observation

AI recommended  = defaultfrom == 'AI'
Service selected = selectedfrom is not empty
AI default kept  = selectedfrom contains 'Default' (rep took what AI pre-filled)
"""

import csv
import sys
import os
from collections import defaultdict

FILE = sys.argv[1] if len(sys.argv) > 1 else '20260329120322330.csv'
OUT  = os.path.join('validation_output',
       'acceptance_' + os.path.splitext(os.path.basename(FILE))[0] + '.txt')

# ── helpers ──────────────────────────────────────────────────────────────────
def is_ai(row):
    return row['defaultfrom'] == 'AI'

def is_selected(row):
    return bool(row['selectedfrom'].strip())

def is_default_kept(row):
    sf = row['selectedfrom']
    return bool(sf) and 'Default' in sf and 'Non-Default' not in sf

# ── collect data ──────────────────────────────────────────────────────────────
# Config-level counters (EMEA, Global)
cfg = {
    'EMEA': {'total': 0, 'ai': 0, 'ai_selected': 0, 'ai_default_kept': 0,
             'non_ai': 0, 'non_ai_selected': 0},
    'Global': {'total': 0, 'ai': 0, 'ai_selected': 0, 'ai_default_kept': 0,
               'non_ai': 0, 'non_ai_selected': 0},
}

# Contract-level: track per contract_number
contracts = {}   # key: (geo_bucket, contract_number)
                 # value: dict with flags

with open(FILE, encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        geo     = row['geo']
        cnum    = row['contract_number']
        ai      = is_ai(row)
        sel     = is_selected(row)
        def_kept = is_default_kept(row)

        buckets = ['Global']
        if geo == 'EMEA':
            buckets.append('EMEA')

        for b in buckets:
            cfg[b]['total'] += 1
            if ai:
                cfg[b]['ai'] += 1
                if sel:       cfg[b]['ai_selected'] += 1
                if def_kept:  cfg[b]['ai_default_kept'] += 1
            else:
                cfg[b]['non_ai'] += 1
                if sel:       cfg[b]['non_ai_selected'] += 1

            key = (b, cnum)
            if key not in contracts:
                contracts[key] = {'has_ai': False, 'ai_selected': False,
                                  'ai_default_kept': False,
                                  'any_selected': False}
            c = contracts[key]
            if ai:
                c['has_ai'] = True
                if sel:       c['ai_selected'] = True
                if def_kept:  c['ai_default_kept'] = True
            if sel:
                c['any_selected'] = True

# ── contract-level aggregation ────────────────────────────────────────────────
ctr = {
    'EMEA':   {'total': 0, 'ai': 0, 'ai_selected': 0, 'ai_default_kept': 0,
               'non_ai': 0, 'non_ai_selected': 0},
    'Global': {'total': 0, 'ai': 0, 'ai_selected': 0, 'ai_default_kept': 0,
               'non_ai': 0, 'non_ai_selected': 0},
}
for (b, _cnum), c in contracts.items():
    ctr[b]['total'] += 1
    if c['has_ai']:
        ctr[b]['ai'] += 1
        if c['ai_selected']:      ctr[b]['ai_selected'] += 1
        if c['ai_default_kept']:  ctr[b]['ai_default_kept'] += 1
    else:
        ctr[b]['non_ai'] += 1
        if c['any_selected']:     ctr[b]['non_ai_selected'] += 1

# ── format output ─────────────────────────────────────────────────────────────
def pct(num, den):
    return f"{num/den*100:.1f}%" if den else "N/A"

def section(title, cd, ct):
    lines = [
        f"\n{'='*60}",
        f"  {title}",
        f"{'='*60}",
        f"{'Metric':<42} {'Config':>8} {'Contract':>10}",
        f"{'-'*60}",
        f"{'Total observations':<42} {cd['total']:>8,} {ct['total']:>10,}",
        "",
        f"  — AI COVERAGE —",
        f"{'  AI-recommended':<42} {cd['ai']:>8,} {ct['ai']:>10,}",
        f"{'  AI coverage rate':<42} {pct(cd['ai'],cd['total']):>8} {pct(ct['ai'],ct['total']):>10}",
        "",
        f"  — SERVICE ATTACHMENT (any service selected) —",
        f"{'  AI rows: service selected':<42} {cd['ai_selected']:>8,} {ct['ai_selected']:>10,}",
        f"{'  AI attachment rate':<42} {pct(cd['ai_selected'],cd['ai']):>8} {pct(ct['ai_selected'],ct['ai']):>10}",
        f"{'  Non-AI rows: service selected':<42} {cd['non_ai_selected']:>8,} {ct['non_ai_selected']:>10,}",
        f"{'  Non-AI attachment rate':<42} {pct(cd['non_ai_selected'],cd['non_ai']):>8} {pct(ct['non_ai_selected'],ct['non_ai']):>10}",
        f"{'  Lift (AI vs Non-AI)':<42} {'':>8} {'':>10}",
        "",
        f"  — AI DEFAULT ACCEPTANCE (rep kept AI's exact pick) —",
        f"{'  AI default kept':<42} {cd['ai_default_kept']:>8,} {ct['ai_default_kept']:>10,}",
        f"{'  AI default acceptance rate':<42} {pct(cd['ai_default_kept'],cd['ai']):>8} {pct(ct['ai_default_kept'],ct['ai']):>10}",
        f"{'  vs. attachment rate (gap)':<42} {'':>8} {'':>10}",
    ]
    # compute lift and gap inline
    ai_att_cfg = cd['ai_selected']/cd['ai']*100 if cd['ai'] else 0
    nai_att_cfg = cd['non_ai_selected']/cd['non_ai']*100 if cd['non_ai'] else 0
    ai_att_ctr = ct['ai_selected']/ct['ai']*100 if ct['ai'] else 0
    nai_att_ctr = ct['non_ai_selected']/ct['non_ai']*100 if ct['non_ai'] else 0
    ai_def_cfg = cd['ai_default_kept']/cd['ai']*100 if cd['ai'] else 0
    ai_def_ctr = ct['ai_default_kept']/ct['ai']*100 if ct['ai'] else 0

    lines[14] = f"{'  Lift (AI vs Non-AI)':<42} {ai_att_cfg-nai_att_cfg:>+7.1f}pp {ai_att_ctr-nai_att_ctr:>+9.1f}pp"
    lines[20] = f"{'  vs. attachment rate (gap)':<42} {ai_att_cfg-ai_def_cfg:>+7.1f}pp {ai_att_ctr-ai_def_ctr:>+9.1f}pp"

    return "\n".join(lines)

output = [
    "SERVICE SMART RECOMMENDATION — ACCEPTANCE & COVERAGE ANALYSIS",
    f"Source: 20260329120322330.csv",
    "",
    "DEFINITIONS",
    "  AI recommended   : defaultfrom = 'AI'",
    "  Service selected : selectedfrom is not empty (any service attached)",
    "  AI default kept  : selectedfrom contains 'Default' (not 'Non-Default')",
    "                     i.e. rep kept the AI pre-filled recommendation",
    "  Config level     : each line_item row = 1 observation",
    "  Contract level   : each unique contract_number = 1 observation",
    "                     contract flagged 'AI' if ANY line item had AI rec",
    "                     contract flagged 'accepted' if ANY line item accepted",
]

output.append(section("EMEA ONLY", cfg['EMEA'], ctr['EMEA']))
output.append(section("GLOBAL (all geos)", cfg['Global'], ctr['Global']))

import os
os.makedirs('validation_output', exist_ok=True)
result = "\n".join(output)
print(result)
with open(OUT, 'w', encoding='utf-8') as f:
    f.write(result)
print(f"\n[Saved to {OUT}]")
