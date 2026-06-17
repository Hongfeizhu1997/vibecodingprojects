"""
EMEA Service Product Analysis by Term and Type
Extract term (1Y-5Y) and service type from PN descriptions.
"""
import openpyxl
from collections import defaultdict, Counter
import re

FILE = "/root/ClaudeProjects/ServiceSmartRecommendationAnalysis/Ai_Report_2026-06-09(4.01-6.01).xlsx"
wb = openpyxl.load_workbook(FILE, data_only=True)
ws = wb["Ai-Report"]

headers = [c.value for c in next(ws.iter_rows(max_row=1))]
col_map = {h: i for i, h in enumerate(headers)}

# ============================================================
# Term extraction patterns
# ============================================================
TERM_PATTERNS = [
    (r'\b(\d+)Y\b', lambda m: int(m.group(1))),      # "3Y"
    (r'\b(\d+)\s*Years?\b', lambda m: int(m.group(1))),  # "3 Years"
    (r'\b(\d+)\s*Year\b', lambda m: int(m.group(1))),     # "3 Year"
]

# Type keywords — ordered by specificity (more specific first)
TYPE_PATTERNS = [
    ('Premier Support Plus', 'Premier Support Plus'),
    ('Premier Support', 'Premier Support'),  # Must come after Plus to avoid false match
    ('Onsite', 'Onsite'),
    ('Basic Warranty', 'Basic Warranty'),
    ('Base Warranty', 'Base Warranty'),
    ('Warranty Extension', 'Warranty Extension'),
    ('Depot', 'Depot'),
    ('Courier', 'Courier'),
    ('Premier', 'Premier (generic)'),
    ('Essential', 'Essential'),
]

def extract_term(desc):
    """Extract year term from description. Returns int or None."""
    if not desc:
        return None
    desc_str = str(desc)
    for pattern, fn in TERM_PATTERNS:
        m = re.search(pattern, desc_str, re.IGNORECASE)
        if m:
            term = fn(m)
            if 1 <= term <= 5:
                return term
    return None

def extract_type(desc):
    """Extract service type from description."""
    if not desc:
        return None
    desc_str = str(desc)
    for keyword, label in TYPE_PATTERNS:
        if keyword.lower() in desc_str.lower():
            return label
    return 'Other/Unknown'

# ============================================================
# Process EMEA data
# ============================================================
# Counters
term_stats = defaultdict(lambda: {'total': 0, 'accepted': 0, 'changed': 0, 'no_select': 0, 'has_default': 0})
type_stats = defaultdict(lambda: {'total': 0, 'accepted': 0, 'changed': 0, 'no_select': 0, 'has_default': 0})
term_type_stats = defaultdict(lambda: {'total': 0, 'accepted': 0, 'changed': 0, 'no_select': 0})
term_type_acceptance = defaultdict(lambda: defaultdict(lambda: {'total': 0, 'accepted': 0}))

# Transition matrix: default term/type → selected term/type
transition_term = defaultdict(Counter)
transition_type = defaultdict(Counter)

for row in ws.iter_rows(min_row=2, values_only=True):
    geo = row[col_map['geo']]
    if geo != 'EMEA':
        continue
    
    dsp = row[col_map['defaultServicePn1']]
    dsp_desc = row[col_map['defaultServicePn1Desc']]
    ssp = row[col_map['selectedServicePn1']]
    ssp_desc = row[col_map['selectedServicePn1Desc']]
    
    has_default = bool(dsp and str(dsp).strip())
    has_selected = bool(ssp and str(ssp).strip())
    
    if not has_default:
        continue
    
    # Extract term and type from DEFAULT recommendation
    d_term = extract_term(dsp_desc)
    d_type = extract_type(dsp_desc)
    
    # Extract term and type from SELECTED service
    s_term = extract_term(ssp_desc) if has_selected else None
    s_type = extract_type(ssp_desc) if has_selected else None
    
    accepted = has_default and has_selected and (str(dsp).strip() == str(ssp).strip())
    changed = has_default and has_selected and (str(dsp).strip() != str(ssp).strip())
    no_select = has_default and not has_selected
    
    # Update term stats
    if d_term:
        tkey = f"{d_term}Y"
        term_stats[tkey]['total'] += 1
        term_stats[tkey]['has_default'] += 1
        if accepted: term_stats[tkey]['accepted'] += 1
        if changed: term_stats[tkey]['changed'] += 1
        if no_select: term_stats[tkey]['no_select'] += 1
        
        if s_term:
            transition_term[tkey][f"{s_term}Y"] += 1
    
    # Update type stats
    if d_type:
        type_stats[d_type]['total'] += 1
        type_stats[d_type]['has_default'] += 1
        if accepted: type_stats[d_type]['accepted'] += 1
        if changed: type_stats[d_type]['changed'] += 1
        if no_select: type_stats[d_type]['no_select'] += 1
        
        if s_type:
            transition_type[d_type][s_type] += 1
    
    # Update term × type
    if d_term and d_type:
        tkey = f"{d_term}Y"
        ttkey = f"{tkey} {d_type}"
        term_type_stats[ttkey]['total'] += 1
        if accepted: term_type_stats[ttkey]['accepted'] += 1
        if changed: term_type_stats[ttkey]['changed'] += 1
        if no_select: term_type_stats[ttkey]['no_select'] += 1
        
        term_type_acceptance[tkey][d_type]['total'] += 1
        if accepted: term_type_acceptance[tkey][d_type]['accepted'] += 1

# ============================================================
# Print Results
# ============================================================
def pct(num, den):
    return f"{num/den*100:.1f}%" if den else "—"

print("="*70)
print("EMEA — SERVICE PRODUCT ANALYSIS BY TERM")
print("="*70)
print(f"{'Term':<8} {'Count':>7} {'Accepted':>8} {'Acc%':>7} {'Changed':>7} {'Chg%':>7} {'NoSelect':>8} {'NS%':>7}")
print("-"*70)
for t in ['1Y','2Y','3Y','4Y','5Y']:
    s = term_stats[t]
    ttl = s['total']
    if ttl == 0: continue
    print(f"{t:<8} {ttl:>7} {s['accepted']:>8} {pct(s['accepted'],ttl):>7} {s['changed']:>8} {pct(s['changed'],ttl):>7} {s['no_select']:>8} {pct(s['no_select'],ttl):>7}")

print("\n" + "="*70)
print("EMEA — SERVICE PRODUCT ANALYSIS BY TYPE")
print("="*70)
print(f"{'Type':<25} {'Count':>7} {'Accepted':>8} {'Acc%':>7} {'Changed':>7} {'Chg%':>7} {'NoSelect':>8} {'NS%':>7}")
print("-"*70)
for tp in sorted(type_stats.keys(), key=lambda k: type_stats[k]['total'], reverse=True):
    s = type_stats[tp]
    ttl = s['total']
    if ttl < 50: continue
    print(f"{tp:<25} {ttl:>7} {s['accepted']:>8} {pct(s['accepted'],ttl):>7} {s['changed']:>8} {pct(s['changed'],ttl):>7} {s['no_select']:>8} {pct(s['no_select'],ttl):>7}")

print("\n" + "="*70)
print("EMEA — TERM × TYPE ACCEPTANCE MATRIX")
print("="*70)
types_sorted = sorted(type_stats.keys(), key=lambda k: type_stats[k]['total'], reverse=True)
terms_sorted = ['1Y','2Y','3Y','4Y','5Y']

# Header
print(f"{'':>8}", end='')
for tp in types_sorted:
    if type_stats[tp]['total'] < 50: continue
    print(f"{tp:>18}", end='')
print()

for t in terms_sorted:
    print(f"{t:<8}", end='')
    for tp in types_sorted:
        if type_stats[tp]['total'] < 50: continue
        data = term_type_acceptance[t][tp]
        if data['total'] >= 20:
            acc = data['accepted']/data['total']*100
            print(f"{acc:>6.1f}% ({data['total']:>5})", end='  ')
        else:
            print(f"{'—':>18}", end='  ')
    print()

print("\n" + "="*70)
print("EMEA — TOP 20 TERM × TYPE COMBINATIONS (by volume)")
print("="*70)
print(f"{'Combination':<40} {'Count':>7} {'Accepted':>8} {'Acc%':>7} {'Changed':>7} {'Chg%':>7}")
print("-"*70)
for combo in sorted(term_type_stats.keys(), key=lambda k: term_type_stats[k]['total'], reverse=True)[:20]:
    s = term_type_stats[combo]
    ttl = s['total']
    print(f"{combo:<40} {ttl:>7} {s['accepted']:>8} {pct(s['accepted'],ttl):>7} {s['changed']:>8} {pct(s['changed'],ttl):>7}")

print("\n" + "="*70)
print("EMEA — TERM TRANSITION MATRIX (default → selected)")
print("="*70)
all_terms = ['1Y','2Y','3Y','4Y','5Y']
label_ds = "Def\\Sel"
print(f"{label_ds:>8}", end='')
for t in all_terms:
    print(f"{t:>8}", end='')
print(f"{'  None':>8}")
for d in all_terms:
    print(f"{d:<8}", end='')
    total_trans = sum(transition_term[d].values())
    for s in all_terms:
        cnt = transition_term[d][f"{s}"]
        print(f"{cnt:>8}", end='')
    # Those who selected but term couldn't be parsed
    none_cnt = term_stats[d]['no_select']
    print(f"{none_cnt:>8}")

print("\n" + "="*70)
print("EMEA — TYPE TRANSITION MATRIX (default → selected, top types)")
print("="*70)
top_types = [t for t in types_sorted if type_stats[t]['total'] >= 100][:8]
label_ds2 = "Def\\Sel"
print(f"{label_ds2:<22}", end='')
for t in top_types:
    print(f"{t:>14}", end='')
print()
for d in top_types:
    print(f"{d:<22}", end='')
    for s in top_types:
        cnt = transition_type[d][s]
        print(f"{cnt:>14}", end='')
    print()

# Also sample some descriptions to validate extraction
print("\n" + "="*70)
print("VALIDATION — Sample PN descriptions and extracted term/type")
print("="*70)
seen = set()
count = 0
for row in ws.iter_rows(min_row=2, values_only=True):
    geo = row[col_map['geo']]
    if geo != 'EMEA': continue
    desc = row[col_map['defaultServicePn1Desc']]
    if not desc or str(desc).strip() in seen: continue
    seen.add(str(desc).strip())
    t = extract_term(desc)
    tp = extract_type(desc)
    print(f"  Term={t}  Type={tp:<22} | {str(desc)[:80]}")
    count += 1
    if count >= 20: break
