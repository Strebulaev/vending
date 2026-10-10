import csv
with open('material/sources-registry.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['status'] == 'failed':
            print(f"{row['track']}/{row['category_guess']}: {row['url']}")
            print(f"  Error: {row['notes']}")