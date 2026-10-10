#!/usr/bin/env python3
"""
Update registry status based on existing downloaded files.
"""
import csv
import os
from pathlib import Path

REGISTRY_PATH = Path('material/sources-registry.csv')
MATERIAL_ROOT = Path('material')

def main():
    if not REGISTRY_PATH.exists():
        print(f"Registry not found: {REGISTRY_PATH}")
        return
    
    rows = []
    with REGISTRY_PATH.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)
    
    # Build index of existing files
    existing = {}
    for root, dirs, files in os.walk(MATERIAL_ROOT):
        for f in files:
            if f == 'sources-registry.csv':
                continue
            full = Path(root) / f
            rel = full.relative_to(MATERIAL_ROOT)
            existing[str(rel)] = str(full)
    
    # Update rows
    for row in rows:
        url = row['url']
        # Generate expected filename
        from urllib.parse import urlparse
        import hashlib
        parsed = urlparse(url)
        domain = parsed.netloc.replace('www.', '')
        path_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        ext = ''
        path = parsed.path
        if '.' in path:
            possible_ext = path.split('.')[-1].split('?')[0].split('#')[0]
            if len(possible_ext) <= 5 and possible_ext.isalnum():
                ext = '.' + possible_ext.lower()
        expected_name = f"{domain}_{path_hash}{ext}"
        
        # Check if file exists in the expected category dir
        category = row['category_guess'] or 'web-archive'
        track = row['track']
        expected_rel = f"{track}/{category}/{expected_name}"
        
        if expected_rel in existing:
            row['local_path'] = expected_rel
            row['status'] = 'downloaded'
            row['notes'] = ''
        else:
            # Try to find by partial match
            matches = [p for p in existing if expected_name in p and track in p]
            if matches:
                row['local_path'] = matches[0]
                row['status'] = 'downloaded'
                row['notes'] = ''
    
    # Write back
    with REGISTRY_PATH.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    downloaded = sum(1 for r in rows if r['status'] == 'downloaded')
    failed = sum(1 for r in rows if r['status'] == 'failed')
    pending = sum(1 for r in rows if r['status'] == 'pending')
    print(f"Registry updated. Downloaded: {downloaded}, Failed: {failed}, Pending: {pending}")

if __name__ == '__main__':
    main()