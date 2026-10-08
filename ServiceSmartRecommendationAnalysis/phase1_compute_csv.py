#!/usr/bin/env python3
"""
SSR Phase 1 — Operational KPI computer for Contract CSV (87-column schema).

Reads contract-level CSV (contract_number + line_item) and computes all Phase 1
metrics by fiscal quarter. Reuses the phase1_compute.py logic, adapted to the
87-column CSV schema where:
  - default_pn / selection_pn  (all-lowercase)
  - default_term / default_servicetype already structured (no regex needed)
  - defaultfrom has extra 'ALL' value
  - contract_creation_date (YYYY-MM-DD ...) is the date column

Usage:
  python3 phase1_compute_csv.py <input.csv> <output_dir>
Outputs:
  <output_dir>/phase1_q1.json   (Apr–Jun)
  <output_dir>/phase1_q2.json   (Jul–Sep)
"""
import csv
import json
import sys
from collections import defaultdict, Counter

def ne(v):
    return bool(v and str(v).strip())

def init_counts():
    return {
        'total': 0, 'has_default': 0, 'ai_default': 0, 'has_selected': 0,
        'accepted': 0, 'changed': 0, 'attach_failure': 0,
        'new_cto': 0, 'copied_cto': 0, 'mtm': 0,
    }

def compute_rates(d):
    t = d['total']; hd = d['has_default']
    return {
        'total': t,
        'coverage': round(hd / t * 100, 1) if t else 0,
        'ai_coverage': round(d['ai_default'] / t * 100, 1) if t else 0,
        'attach': round(d['has_selected'] / t * 100, 1) if t else 0,
        'acceptance': round(d['accepted'] / hd * 100, 1) if hd else 0,
        'change': round(d['changed'] / hd * 100, 1) if hd else 0,
        'attach_failure': round(d['attach_failure'] / hd * 100, 1) if hd else 0,
        'no_default': round((t - hd) / t * 100, 1) if t else 0,
        'influence': round((d['accepted'] + d['changed']) / hd * 100, 1) if hd else 0,
        'has_default': hd, 'has_selected': d['has_selected'],
        'accepted': d['accepted'], 'changed': d['changed'],
        'new_cto': d['new_cto'], 'copied_cto': d['copied_cto'], 'mtm': d['mtm'],
    }

def add_row(d, row, has_default, has_selected, is_ai, accepted, changed, attach_fail):
    d['total'] += 1
    if has_default: d['has_default'] += 1
    if is_ai: d['ai_default'] += 1
    if has_selected: d['has_selected'] += 1
    if accepted: d['accepted'] += 1
    if changed: d['changed'] += 1
    if attach_fail: d['attach_failure'] += 1

def quarter_of(date10):
    m = int(date10[5:7])
    if 1 <= m <= 3: return 'Q4'  # FY Q4 (Jan–Mar)
    if 4 <= m <= 6: return 'Q1'
    if 7 <= m <= 9: return 'Q2'
    return None  # Q3 (Oct–Dec) or out of scope

def analyze(filepath):
    rows = []
    with open(filepath, encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            rows.append(r)

    # split by quarter
    quarters = {'Q1': [], 'Q2': [], 'Q4': []}
    for r in rows:
        d = r.get('contract_creation_date', '')[:10]
        q = quarter_of(d) if d else None
        if q in quarters:
            quarters[q].append(r)

    result = {}
    for q in ('Q1', 'Q2', 'Q4'):
        qrows = quarters[q]
        overall = init_counts()
        geo_data = defaultdict(init_counts)
        origin_data = defaultdict(init_counts)      # configuredfrom
        src_data = defaultdict(init_counts)         # defaultfrom
        month_data = defaultdict(init_counts)
        geo_month = defaultdict(lambda: defaultdict(init_counts))
        geo_origin = defaultdict(lambda: defaultdict(init_counts))
        country_data = defaultdict(init_counts)     # endcustomercountry per GEO
        geo_country = defaultdict(lambda: defaultdict(init_counts))
        geo_source = defaultdict(lambda: defaultdict(init_counts))  # GEO x defaultfrom

        for r in qrows:
            geo = (r.get('geo') or '').strip()
            cf = (r.get('configuredfrom') or '').strip()
            src = (r.get('defaultfrom') or '').strip()
            dsp = r.get('default_pn'); ssp = r.get('selection_pn')
            country = (r.get('endcustomercountry') or '').strip()
            m = (r.get('contract_creation_date') or '')[:7]

            if not geo:
                continue

            has_default = ne(dsp)
            has_selected = ne(ssp)
            is_ai = (src == 'AI')
            accepted = has_default and has_selected and (str(dsp).strip() == str(ssp).strip())
            changed = has_default and has_selected and (str(dsp).strip() != str(ssp).strip())
            attach_fail = has_default and not has_selected

            add_row(overall, r, has_default, has_selected, is_ai, accepted, changed, attach_fail)
            gd = geo_data[geo]
            add_row(gd, r, has_default, has_selected, is_ai, accepted, changed, attach_fail)
            if cf == 'New CTO': gd['new_cto'] += 1
            elif cf == 'Copied CTO': gd['copied_cto'] += 1
            elif cf == 'MTM': gd['mtm'] += 1
            if cf == 'New CTO': overall['new_cto'] += 1
            elif cf == 'Copied CTO': overall['copied_cto'] += 1
            elif cf == 'MTM': overall['mtm'] += 1

            if cf:
                od = origin_data[cf]
                add_row(od, r, has_default, has_selected, is_ai, accepted, changed, attach_fail)
            if src:
                sd = src_data[src]
                add_row(sd, r, has_default, has_selected, is_ai, accepted, changed, attach_fail)
            if m:
                md = month_data[m]
                add_row(md, r, has_default, has_selected, is_ai, accepted, changed, attach_fail)
                gm = geo_month[geo][m]
                add_row(gm, r, has_default, has_selected, is_ai, accepted, changed, attach_fail)
            if geo and cf:
                go = geo_origin[geo][cf]
                go['total'] += 1
                if has_default: go['has_default'] += 1
                if has_selected: go['has_selected'] += 1
                if accepted: go['accepted'] += 1
                if changed: go['changed'] += 1
                if attach_fail: go['attach_failure'] += 1
            if country:
                cd = geo_country[geo][country]
                cd['total'] += 1
                if has_default: cd['has_default'] += 1
                if is_ai: cd['ai_default'] += 1
                if has_selected: cd['has_selected'] += 1
                if accepted: cd['accepted'] += 1
                if changed: cd['changed'] += 1
                if attach_fail: cd['attach_failure'] += 1
            if src:
                gs = geo_source[geo][src]
                add_row(gs, r, has_default, has_selected, is_ai, accepted, changed, attach_fail)

        result[q] = {
            'overall': compute_rates(overall),
            'geo': {g: compute_rates(geo_data[g]) for g in sorted(geo_data)},
            'origin': {o: compute_rates(origin_data[o]) for o in sorted(origin_data)},
            'source': {s: compute_rates(src_data[s]) for s in sorted(src_data)},
            'month': {m: compute_rates(month_data[m]) for m in sorted(month_data)},
            'geo_month': {g: {m: compute_rates(geo_month[g][m]) for m in sorted(geo_month[g])} for g in sorted(geo_month)},
            'geo_origin': {g: {o: compute_rates(geo_origin[g][o]) for o in sorted(geo_origin[g])} for g in sorted(geo_origin)},
            'country': {g: {c: compute_rates(geo_country[g][c]) for c in sorted(geo_country[g], key=lambda c: -geo_country[g][c]['total'])} for g in sorted(geo_country)},
            'geo_source': {g: {s: compute_rates(geo_source[g][s]) for s in sorted(geo_source[g])} for g in sorted(geo_source)},
        }

    return result

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 phase1_compute_csv.py <input.csv> <output_dir>")
        sys.exit(1)
    filepath = sys.argv[1]
    outdir = sys.argv[2] if len(sys.argv) > 2 else '.'
    res = analyze(filepath)

    for q in ('Q1', 'Q2', 'Q4'):
        if res[q]['overall']['total'] == 0:
            continue
        out = f"{outdir}/phase1_{q.lower()}.json"
        with open(out, 'w') as f:
            json.dump(res[q], f, indent=2, default=str)
        ov = res[q]['overall']
        print(f"\n===== {q} =====")
        print(f"Total: {ov['total']:,}  Coverage: {ov['coverage']}%  AI Cov: {ov['ai_coverage']}%")
        print(f"Attach: {ov['attach']}%  Acceptance: {ov['acceptance']}%  Change: {ov['change']}%  Att.Fail: {ov['attach_failure']}%")
        print(f"Saved: {out}")
