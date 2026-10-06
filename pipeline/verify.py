import os
import re
import sys

def has_cyrillic(text):
    """Check if text contains Cyrillic characters (U+0400 to U+04FF)."""
    return bool(re.search(r'[\u0400-\u04FF]', text))

def has_transliteration_patterns(text):
    """Check for known Serbian/Latin transliteration patterns from Cyrillic.
    
    Characteristic patterns: Lj/Nj/Dz as standalone Latin mappings of 
    Cyrillic Љ/Њ/Ђ. These are checked with word boundaries to avoid
    false positives with normal English words containing 'lj', 'nj', 'dz'.
    """
    # Check for characteristic transliteration patterns
    # These patterns must appear as recognizable markers, not within English words
    patterns = [
        r'(?<![a-zA-Z])lj(?![a-zA-Z])',    # standalone lj
        r'(?<![a-zA-Z])nj(?![a-zA-Z])',    # standalone nj
        r'(?<![a-zA-Z])dz(?![a-zA-Z])',    # standalone dz
    ]
    
    for p in patterns:
        if re.search(p, text, re.IGNORECASE):
            return True
    return False

# Collect all .md files under pipeline/
pipeline_dir = 'docs/pipeline'
errors = []
ok_files = []

for root, dirs, files in os.walk(pipeline_dir):
    for fname in sorted(files):
        if fname.endswith('.md'):
            fpath = os.path.join(root, fname)
            try:
                with open(fpath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                has_cyr = has_cyrillic(content)
                has_trans = has_transliteration_patterns(content)
                
                if has_cyr or has_trans:
                    errors.append(fpath)
                else:
                    ok_files.append(fpath)
                    print(f'OK {fpath}')
            except Exception as e:
                errors.append(fpath)
                print(f'ERROR {fpath}: {e}')

print()
print(f'Total files checked: {len(ok_files) + len(errors)}')
print(f'OK: {len(ok_files)}, Errors: {len(errors)}')

if errors:
    print('\\nOffending files:')
    for fpath in sorted(errors):
        print(f'  - {fpath}')
    sys.exit(1)
else:
    print('\\nAll files OK - no Cyrillic or transliteration patterns found.')
    sys.exit(0)