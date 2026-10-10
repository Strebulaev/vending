#!/usr/bin/env python3
"""
Download and archive sources from the registry.
Saves to material/{track}/{category_guess}/
Updates registry with local_path and status.
"""
import csv
import os
import sys
import time
import hashlib
import mimetypes
from pathlib import Path
from urllib.parse import urlparse
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

REGISTRY_PATH = Path('material/sources-registry.csv')
MATERIAL_ROOT = Path('material')

# Session with retries
session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
session.mount('http://', HTTPAdapter(max_retries=retries))
session.mount('https://', HTTPAdapter(max_retries=retries))
session.headers.update({'User-Agent': 'Mozilla/5.0 (compatible; VendingBot/1.0)'})

def safe_filename(url: str, track: str, category: str) -> str:
    """Generate a safe filename from URL."""
    parsed = urlparse(url)
    # Use domain + path hash
    domain = parsed.netloc.replace('www.', '')
    path_hash = hashlib.md5(url.encode()).hexdigest()[:8]
    ext = ''
    # Try to guess extension from URL path
    path = parsed.path
    if '.' in path:
        possible_ext = path.split('.')[-1].split('?')[0].split('#')[0]
        if len(possible_ext) <= 5 and possible_ext.isalnum():
            ext = '.' + possible_ext.lower()
    # Fallback: try content-type later
    return f"{domain}_{path_hash}{ext}"

def download_url(url: str, dest_path: Path, timeout=30) -> tuple[bool, str]:
    """Download URL to dest_path. Returns (success, error_message)."""
    try:
        resp = session.get(url, timeout=timeout, stream=True, allow_redirects=True)
        resp.raise_for_status()
        
        # Check content-type for extension
        content_type = resp.headers.get('Content-Type', '').split(';')[0].strip()
        if not dest_path.suffix and content_type:
            guessed_ext = mimetypes.guess_extension(content_type)
            if guessed_ext:
                dest_path = dest_path.with_suffix(guessed_ext)
        
        # Write file
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        with dest_path.open('wb') as f:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        return True, ''
    except Exception as e:
        return False, str(e)

def main():
    if not REGISTRY_PATH.exists():
        print(f"Registry not found: {REGISTRY_PATH}")
        sys.exit(1)
    
    rows = []
    with REGISTRY_PATH.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    fieldnames = reader.fieldnames
    
    # Filter pending downloads
    pending = [r for r in rows if r['status'] == 'pending']
    print(f"Total rows: {len(rows)}, Pending: {len(pending)}")
    
    # Group by track/category for progress
    for i, row in enumerate(pending, 1):
        track = row['track']
        category = row['category_guess'] or 'web-archive'
        url = row['url']
        
        dest_dir = MATERIAL_ROOT / track / category
        filename = safe_filename(url, track, category)
        dest_path = dest_dir / filename
        
        # Avoid overwriting existing files
        counter = 1
        original_dest = dest_path
        while dest_path.exists():
            stem = original_dest.stem
            suffix = original_dest.suffix
            dest_path = dest_dir / f"{stem}_{counter}{suffix}"
            counter += 1
        
        print(f"[{i}/{len(pending)}] {track}/{category} <- {url[:80]}...")
        success, error = download_url(url, dest_path)
        
        row['local_path'] = str(dest_path.relative_to(MATERIAL_ROOT)) if success else ''
        row['status'] = 'downloaded' if success else 'failed'
        row['notes'] = error if not success else ''
        
        if not success:
            print(f"  FAILED: {error}")
        else:
            print(f"  OK -> {dest_path.name} ({dest_path.stat().st_size} bytes)")
        
        # Be nice to servers
        time.sleep(0.5)
    
    # Write back updated registry
    with REGISTRY_PATH.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    # Summary
    downloaded = sum(1 for r in rows if r['status'] == 'downloaded')
    failed = sum(1 for r in rows if r['status'] == 'failed')
    print(f"\nDone. Downloaded: {downloaded}, Failed: {failed}, Pending: {sum(1 for r in rows if r['status'] == 'pending')}")

if __name__ == '__main__':
    main()