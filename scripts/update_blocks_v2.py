#!/usr/bin/env python3
"""
Update cost-estimate blocks to use local material paths instead of external URLs.
Handles URLs with trailing text like "(page opened 2026-10-08)".
"""
import re
from pathlib import Path
import csv

# Load URL to local path mapping
url_to_local = {}
with open('material/sources-registry.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['status'] == 'downloaded' and row['local_path']:
            url_to_local[row['url']] = row['local_path']

def normalize_url(url):
    return url.rstrip('/').rstrip('.')

url_to_local_norm = {normalize_url(k): v for k, v in url_to_local.items()}

# Also create a mapping of domain+path for fuzzy matching
def url_key(url):
    parsed = re.sub(r'^https?://', '', url)
    parsed = parsed.rstrip('/').rstrip('.')
    return parsed.lower()

url_to_local_fuzzy = {url_key(k): v for k, v in url_to_local.items()}

BLOCKS_DIR = Path('docs/cost-estimates/blocks')

def find_local_path(url_text):
    """Find local path for a URL that may have trailing text."""
    # Extract just the URL part (http... until space, ), ;, or end)
    match = re.search(r'(https?://[^\s\);]+)', url_text)
    if not match:
        return None
    url = match.group(1).rstrip('.,;)')
    
    # Try exact match
    norm = normalize_url(url)
    if norm in url_to_local_norm:
        return url_to_local_norm[norm]
    
    # Try fuzzy match (domain + path)
    key = url_key(url)
    if key in url_to_local_fuzzy:
        return url_to_local_fuzzy[key]
    
    # Try without www.
    key_no_www = key.replace('www.', '')
    if key_no_www in url_to_local_fuzzy:
        return url_to_local_fuzzy[key_no_www]
    
    return None

def replace_urls_in_block(content: str) -> str:
    """Replace external URLs in source column with local paths."""
    lines = content.split('\n')
    new_lines = []
    
    for line in lines:
        def replace_match(match):
            prefix = match.group(1)
            urls_text = match.group(2)
            suffix = match.group(3)
            
            # Split by semicolon to get individual URLs
            urls = [u.strip() for u in urls_text.split(';')]
            new_urls = []
            
            for url in urls:
                local_path = find_local_path(url)
                if local_path:
                    local_path = local_path.replace('\\', '/')
                    new_urls.append(f"`material/{local_path}`")
                else:
                    new_urls.append(url)
            
            return f"{prefix}{'; '.join(new_urls)}{suffix}"
        
        # Pattern: [source: ...] at end of line or before ]
        new_line = re.sub(r'(\[source:\s*)([^\]]+)(\])', replace_match, line)
        new_lines.append(new_line)
    
    return '\n'.join(new_lines)

def main():
    block_files = list(BLOCKS_DIR.glob('*.md'))
    print(f"Processing {len(block_files)} block files...")
    
    for block_file in block_files:
        content = block_file.read_text(encoding='utf-8')
        new_content = replace_urls_in_block(content)
        
        if new_content != content:
            block_file.write_text(new_content, encoding='utf-8')
            print(f"  Updated: {block_file.name}")
        else:
            print(f"  No changes: {block_file.name}")

if __name__ == '__main__':
    main()