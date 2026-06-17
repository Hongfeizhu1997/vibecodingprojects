import csv

geo_set = set()
country_set = set()
selectedfrom_set = set()
currency_set = set()
dates = []
rows_with_ai = 0
rows_with_selection_price = 0
total = 0

with open('20260329120322330.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        total += 1
        geo_set.add(row.get('geo', ''))
        country_set.add(row.get('endcustomercountry', ''))
        selectedfrom_set.add(row.get('selectedfrom', ''))
        currency_set.add(row.get('currency', ''))
        d = row.get('contract_creation_date', '')
        if d:
            dates.append(d[:10])
        if row.get('selectedfrom') == 'AI':
            rows_with_ai += 1
        if row.get('selection_salesprice'):
            rows_with_selection_price += 1

print('Total rows:', total)
print('Geo values:', sorted(geo_set))
print('Countries (' + str(len(country_set)) + '):', sorted(country_set))
print('Selectedfrom values:', sorted(selectedfrom_set))
print('Currencies:', sorted(currency_set))
print('Date range:', min(dates), 'to', max(dates))
print('AI rows:', rows_with_ai)
print('Rows with selection_salesprice:', rows_with_selection_price)
