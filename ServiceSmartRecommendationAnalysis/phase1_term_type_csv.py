#!/usr/bin/env python3
"""
SSR Phase 1 — Term x Type analysis for Contract CSV (87-col).

CSV already has structured default_term / default_servicetype (no regex needed).
This normalizes them:
  - term: 'One Year'..'Five Year' -> 1Y..5Y
  - type: collapse 'AI' suffix variants and group add-on services.

Usage: python3 phase1_term_type_csv.py <input.csv> <output_dir>
Outputs: <output_dir>/term_type_q1.json, term_type_q2.json
"""
import csv
import json
import sys
from collections import defaultdict

TERM_MAP = {'One Year': '1Y', 'Two Year': '2Y', 'Three Year': '3Y',
            'Four Year': '4Y', 'Five Year': '5Y'}

def normalize_type(st):
    st = (st or '').strip()
    if st in ('Premier Support AI', 'Premier'):
        return 'Premier Support'
    if st in ('Premier Support Plus AI', 'Premier Support Plus'):
        return 'Premier Support Plus'
    if st in ('Onsite', 'Onsite EDU'):
        return 'Onsite'
    if st in ('Depot', 'Depot EDU', 'Mail-in'):
        return 'Depot / Mail-in'
    if st in ('CO2', 'KYD', 'ADP', 'SBTY', 'TICRU', 'INTL', 'PremiumCare',
              'Lenovo Education Support'):
        return 'Other / Add-on'
    return None

def ne(v):
    return bool(v and str(v).strip())

def quarter_of(date10):
    m = int(date10[5:7])
    if 1 <= m <= 3: return 'Q4'  # FY Q4 (Jan–Mar)
    if 4 <= m <= 6: return 'Q1'
    if 7 <= m <= 9: return 'Q2'
    return None

def analyze(filepath):
    # structure: [geo][term][type] = {'total','accepted','changed','att_fail'}
    quarters = {'Q1': defaultdict(lambda: defaultdict(lambda: defaultdict(
        lambda: {'total':0,'accepted':0,'changed':0,'att_fail':0}))),
                'Q2': defaultdict(lambda: defaultdict(lambda: defaultdict(
        lambda: {'total':0,'accepted':0,'changed':0,'att_fail':0}))),
                'Q4': defaultdict(lambda: defaultdict(lambda: defaultdict(
        lambda: {'total':0,'accepted':0,'changed':0,'att_fail':0})))}

    with open(filepath, encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            d = (r.get('contract_creation_date') or '')[:10]
            q = quarter_of(d) if d else None
            if q not in quarters:
                continue
            geo = (r.get('geo') or '').strip()
            if not geo:
                continue
            dsp = r.get('default_pn')
            if not ne(dsp):
                continue
            term = TERM_MAP.get((r.get('default_term') or '').strip())
            typ = normalize_type(r.get('default_servicetype'))
            if not term and not typ:
                continue
            ssp = r.get('selection_pn')
            has_sel = ne(ssp)
            accepted = has_sel and (str(dsp).strip() == str(ssp).strip())
            changed = has_sel and (str(dsp).strip() != str(ssp).strip())
            att_fail = not has_sel

            cell = quarters[q][geo][term][typ]
            cell['total'] += 1
            if accepted: cell['accepted'] += 1
            if changed: cell['changed'] += 1
            if att_fail: cell['att_fail'] += 1

    result = {}
    for q in ('Q1', 'Q2', 'Q4'):
        out = {}
        for geo, term_dict in quarters[q].items():
            out[geo] = {}
            for term, type_dict in term_dict.items():
                out[geo][term] = {}
                for typ, cell in type_dict.items():
                    t = cell['total']
                    out[geo][term][typ] = {
                        'total': t,
                        'acceptance': round(cell['accepted'] / t * 100, 1) if t else 0,
                        'change': round(cell['changed'] / t * 100, 1) if t else 0,
                        'att_fail': round(cell['att_fail'] / t * 100, 1) if t else 0,
                    }
        result[q] = out
    return result

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 phase1_term_type_csv.py <input.csv> <output_dir>")
        sys.exit(1)
    filepath = sys.argv[1]
    outdir = sys.argv[2] if len(sys.argv) > 2 else '.'
    res = analyze(filepath)
    for q in ('Q1', 'Q2', 'Q4'):
        if not res[q]:
            continue
        out = f"{outdir}/term_type_{q.lower()}.json"
        with open(out, 'w') as f:
            json.dump(res[q], f, indent=2, default=str)
        print(f"Saved: {out}")
        for geo in sorted(res[q]):
            terms = res[q][geo]
            n = sum(c['total'] for td in terms.values() for c in td.values())
            print(f"  {q} {geo}: {n:,} configs with parsed term/type")
