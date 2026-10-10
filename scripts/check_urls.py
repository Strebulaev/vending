import csv
with open('material/sources-registry.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if 'jmpukui' in row['url'] or 'usa_en' in row['url'] or 'nayax.com/vpos' in row['url']:
            print(f"{row['url']} -> {row['local_path']} ({row['status']})")