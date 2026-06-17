import csv
from collections import Counter

defaultfrom_counter = Counter()
geo_emea_countries = set()
total_emea = 0
emea_with_selection_price = 0

with open('20260329120322330.csv', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    cols = reader.fieldnames
    print("Total columns:", len(cols))
    print("Column names:")
    for i, c in enumerate(cols):
        print(f"  {i+1}: {c}")

    for row in reader:
        df = row.get('defaultfrom', '')
        defaultfrom_counter[df] += 1
        if row.get('geo') == 'EMEA':
            total_emea += 1
            geo_emea_countries.add(row.get('endcustomercountry', ''))
            if row.get('selection_salesprice'):
                emea_with_selection_price += 1

print("\ndefaultfrom values:", defaultfrom_counter.most_common(20))
print(f"\nTotal EMEA rows: {total_emea}")
print(f"EMEA countries ({len(geo_emea_countries)}): {sorted(geo_emea_countries)}")
print(f"EMEA rows with selection_salesprice: {emea_with_selection_price}")
