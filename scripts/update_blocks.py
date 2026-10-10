#!/usr/bin/env python3
"""
Update cost-estimate blocks to use local material paths instead of external URLs.
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

# Also handle URLs that might have slight variations (trailing slashes, etc.)
def normalize_url(url):
    return url.rstrip('/').rstrip('.')

url_to_local_norm = {normalize_url(k): v for k, v in url_to_local.items()}

BLOCKS_DIR = Path('docs/cost-estimates/blocks')

def replace_urls_in_block(content: str) -> str:
    """Replace external URLs in source column with local paths."""
    lines = content.split('\n')
    new_lines = []
    
    for line in lines:
        # Look for URLs in the source column (after [source: )
        # Pattern: [source: URL1 ; URL2 ...] or [source: URL]
        def replace_match(match):
            prefix = match.group(1)
            urls_text = match.group(2)
            suffix = match.group(3)
            
            # Split by semicolon to get individual URLs
            urls = [u.strip() for u in urls_text.split(';')]
            new_urls = []
            
            for url in urls:
                # Remove any trailing punctuation
                url_clean = url.rstrip(').,;')
                norm = normalize_url(url_clean)
                if norm in url_to_local_norm:
                    local_path = url_to_local_norm[norm]
                    # Convert backslashes to forward slashes for markdown
                    local_path = local_path.replace('\\', '/')
                    new_urls.append(f"`material/{local_path}`")
                else:
                    new_urls.append(url)
            
            return f"{prefix}{'; '.join(new_urls)}{suffix}"
        
        # Pattern: [source: ...] at end of line or before ]
        # This matches [source: URL] or [source: URL1; URL2]
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