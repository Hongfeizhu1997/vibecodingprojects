"""
Load historical benchmarks from old Excel GEO summary sheets and previous reports.
"""
import openpyxl
import json

OLD_FILE = "/root/ClaudeProjects/ServiceSmartRecommendationAnalysis/Ai_Report_20250815~20260306.xlsx"

wb = openpyxl.load_workbook(OLD_FILE, read_only=True, data_only=True)

# Load the GEO summary sheets
for sheet_name in ['GEO（11.28-03.06)', 'GEO（08.15-03.06)']:
    ws = wb[sheet_name]
    print(f"\n{'='*80}")
    print(f"SHEET: {sheet_name}")
    print(f"{'='*80}")
    
    for i, row in enumerate(ws.iter_rows(values_only=True)):
        vals = [str(v)[:50] if v is not None else '' for v in row]
        # Skip empty rows
        if not any(v for v in vals):
            continue
        print(' | '.join(vals))
        if i > 60:
            break

wb.close()
