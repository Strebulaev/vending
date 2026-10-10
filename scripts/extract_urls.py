#!/usr/bin/env python3
"""
Extract all URLs from markdown files in docs/{track}/ directories.
Output a CSV registry: track, source_file, url, context_line, category_guess
"""
import re
import csv
import os
from pathlib import Path

URL_PATTERN = re.compile(r'(https?://[^\s\)\]\}>]+)')

TRACKS = ['hardware', 'economics', 'certification', 'sampling']
DOCS_ROOT = Path('docs')

def guess_category(url: str, context: str) -> str:
    """Heuristic category guess based on URL and surrounding text."""
    url_lower = url.lower()
    context_lower = context.lower()
    
    if any(x in url_lower for x in ['alibaba', 'made-in-china', 'global sources', 'supplier', 'quote', 'price', 'pricing', 'cost', 'fob', 'cif', 'freight', 'shipping', 'logistics']):
        return 'prices'
    if any(x in url_lower for x in ['paragraf.rs', 'sluzbeniglasnik', 'pravilnik', 'zakon', ' zakon', 'regulation', 'standard', 'iso ', 'iec ', 'astm', 'nen', 'gost', 'eur-lex', 'europa.eu', 'gov.rs', 'mduls.gov.rs', 'zdravlje.gov.rs', 'privreda.gov.rs', 'ratel.rs', 'dmdm.gov.rs', 'batut.org.rs', 'gzzjz.org.rs', 'bvk.rs', 'beograd.rs', 'surcin.rs']):
        return 'documents'
    if any(x in url_lower for x in ['certificate', 'accredit', 'protocol', 'lab', 'laboratory', 'test', 'calibration', 'verification', 'declaration', 'conformity']):
        return 'certificates'
    if any(x in context_lower for x in ['calculation', 'formula', 'model', 'spreadsheet', 'excel', 'csv', 'compute', 'estimate']):
        return 'calculations'
    if any(x in context_lower for x in ['letter', 'email', 'meeting', 'call', 'response', 'answer', 'official', 'inquiry', 'request', 'correspondence']):
        return 'correspondence'
    return 'web-archive'

def extract_urls_from_file(filepath: Path, track: str):
    """Extract URLs from a single markdown file."""
    results = []
    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return results
    
    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        for match in URL_PATTERN.finditer(line):
            url = match.group(1).rstrip('.,;)')
            category = guess_category(url, line)
            results.append({
                'track': track,
                'source_file': str(filepath.relative_to(DOCS_ROOT)),
                'url': url,
                'line_number': i,
                'context': line.strip()[:200],
                'category_guess': category
            })
    return results

def main():
    all_results = []
    for track in TRACKS:
        track_path = DOCS_ROOT / track
        if not track_path.exists():
            print(f"Track directory not found: {track_path}")
            continue
        for md_file in track_path.rglob('*.md'):
            results = extract_urls_from_file(md_file, track)
            all_results.extend(results)
            if results:
                print(f"{md_file}: {len(results)} URLs")
    
    # Write CSV
    output_path = Path('material/sources-registry.csv')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['track', 'source_file', 'url', 'line_number', 'context', 'category_guess', 'local_path', 'status', 'notes'])
        writer.writeheader()
        for row in all_results:
            writer.writerow({**row, 'local_path': '', 'status': 'pending', 'notes': ''})
    
    print(f"\nTotal URLs extracted: {len(all_results)}")
    print(f"Registry written to: {output_path}")

if __name__ == '__main__':
    main()