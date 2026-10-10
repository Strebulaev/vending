#!/usr/bin/env python3
"""
Add GRANTS_AND_SUPPORT URLs to registry and download them.
"""
import csv
from pathlib import Path

REGISTRY_PATH = Path('material/sources-registry.csv')

# URLs from GRANTS_AND_SUPPORT.md
new_urls = [
    {
        'track': 'economics',
        'source_file': 'cost-estimates/blocks/GRANTS_AND_SUPPORT.md',
        'url': 'https://biznis.rs/vesti/srbija/drzava-nudi-subvencije-do-380-000-dinara-za-samozaposljavanje-u-2026/',
        'line_number': 5,
        'context': 'Subsidija za samozapošljavanje',
        'category_guess': 'web-archive',
    },
    {
        'track': 'economics',
        'source_file': 'cost-estimates/blocks/GRANTS_AND_SUPPORT.md',
        'url': 'https://biznis.rs/vesti/srbija/drzava-daje-do-18-miliona-dinara-povratnicima-iz-inostranstva-za-pokretanje-i-razvoj-biznisa/',
        'line_number': 6,
        'context': 'Vrati se i stvaraj',
        'category_guess': 'web-archive',
    },
    {
        'track': 'economics',
        'source_file': 'cost-estimates/blocks/GRANTS_AND_SUPPORT.md',
        'url': 'https://ras.gov.rs/javni-poziv-program-kapital-za-razvoj',
        'line_number': 7,
        'context': 'Kapital za razvoj',
        'category_guess': 'documents',
    },
    {
        'track': 'economics',
        'source_file': 'cost-estimates/blocks/GRANTS_AND_SUPPORT.md',
        'url': 'https://www.podunavlje.info/dir/2026/10/08/produzen-rok-za-subvencionisane-kredite-do-30-novembra/',
        'line_number': 7,
        'context': 'Kapital za razvoj deadline',
        'category_guess': 'web-archive',
    },
    {
        'track': 'economics',
        'source_file': 'cost-estimates/blocks/GRANTS_AND_SUPPORT.md',
        'url': 'https://naled.rs/en/vest-jos-pola-miliona-dolara-za-inovacije-otvoren-novi-startech-konkurs-10575',
        'line_number': 8,
        'context': 'StarTech',
        'category_guess': 'web-archive',
    },
    {
        'track': 'economics',
        'source_file': 'cost-estimates/blocks/GRANTS_AND_SUPPORT.md',
        'url': 'https://biznis.rs/preduzetnik/za-razvoj-inovativnih-ideja-do-54-miliona-dinara-po-projektu/',
        'line_number': 9,
        'context': 'Smart Start',
        'category_guess': 'web-archive',
    },
    {
        'track': 'economics',
        'source_file': 'cost-estimates/blocks/GRANTS_AND_SUPPORT.md',
        'url': 'https://biznis.kurir.rs/info-biz/9976926/predstavljen-program-za-pocetnike-u-poslovanju',
        'line_number': 10,
        'context': 'Program for business starters',
        'category_guess': 'web-archive',
    },
]

def main():
    # Read existing registry
    rows = []
    with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)
    
    # Check if URLs already exist
    existing_urls = {row['url'] for row in rows}
    
    # Add new URLs
    for new in new_urls:
        if new['url'] not in existing_urls:
            rows.append({
                'track': new['track'],
                'source_file': new['source_file'],
                'url': new['url'],
                'line_number': new['line_number'],
                'context': new['context'],
                'category_guess': new['category_guess'],
                'local_path': '',
                'status': 'pending',
                'notes': ''
            })
            print(f"Added: {new['url']}")
        else:
            print(f"Already exists: {new['url']}")
    
    # Write back
    with open(REGISTRY_PATH, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"Total rows: {len(rows)}")

if __name__ == '__main__':
    main()