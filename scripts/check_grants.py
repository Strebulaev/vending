import csv
with open('material/sources-registry.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if any(x in row['url'] for x in ['biznis.rs/vesti/srbija/drzava-nudi-subvencije', 'biznis.rs/vesti/srbija/drzava-daje-do-18-miliona', 'ras.gov.rs/javni-poziv', 'naled.rs/en/vest', 'biznis.rs/preduzetnik/za-razvoj', 'biznis.kurir.rs/info-biz/9976926']):
            print(f"{row['url']} -> {row['local_path']} ({row['status']})")