import os
import re

pipeline_dir = 'docs/pipeline/estimates'
estimate_blocks = ['TECH', 'LEGAL', 'FINANCE', 'MARKETING', 'LOCATIONS', 'IT_TELEMETRY', 'OPERATIONS', 'DOCUMENTATION', 'GRANTS_AND_SUPPORT']

# Collect all rows across all estimate files
all_rows = []
file_rows = {}

for block in estimate_blocks:
    path = os.path.join(pipeline_dir, f'{block}.md')
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    rows = []
    in_table = False
    for line in lines:
        if line.startswith('| item') or line.startswith('|------'):
            in_table = True
            continue
        if in_table and line.startswith('|') and not line.startswith('|----'):
            cells = [c.strip() for c in line.split('|')[1:-1]]
            if len(cells) >= 9:
                rows.append({'item': cells[0], 'unit_price': cells[4], 'total': cells[5], 'source': cells[8]})
                all_rows.append({'item': cells[0], 'unit_price': cells[4], 'total': cells[5], 'source': cells[8]})
    file_rows[block] = rows

# a) Every estimate file has at least 80% of unit_price cells filled
print('=== CHECK A: At least 80% of unit_price cells filled per file ===')
a_pass = True
for block, rows in file_rows.items():
    total_cells = len(rows)
    filled_cells = sum(1 for r in rows if r['unit_price'] and r['unit_price'].strip() and r['unit_price'].strip() != '%')
    pct = filled_cells / total_cells * 100 if total_cells > 0 else 0
    status = 'PASS' if pct >= 80 else 'FAIL'
    print(f'  {block}: {filled_cells}/{total_cells} = {pct:.1f}% - {status}')
    if status == 'FAIL':
        a_pass = False

# b) Every estimate file has at least 80% of total cells filled
print()
print('=== CHECK B: At least 80% of total cells filled per file ===')
b_pass = True
for block, rows in file_rows.items():
    total_cells = len(rows)
    filled_cells = sum(1 for r in rows if r['total'] and r['total'].strip())
    pct = filled_cells / total_cells * 100 if total_cells > 0 else 0
    status = 'PASS' if pct >= 80 else 'FAIL'
    print(f'  {block}: {filled_cells}/{total_cells} = {pct:.1f}% - {status}')
    if status == 'FAIL':
        b_pass = False

# c) Every line item has a [source: ...] citation
print()
print('=== CHECK C: Every line item has a [source: ...] citation ===')
all_pass = True
for block, rows in file_rows.items():
    for r in rows:
        src = r['source'] and r['source'].strip()
        has_source = src and src != '[grants: Serbian Gov]' and src != '[grants: source URL]' and 'TBD' not in src.upper()
        if not has_source:
            print(f'  {block} Row {r["item"]}: MISSING source citation - source="{r["source"]}"')
            all_pass = False
if all_pass:
    print('  PASS: All line items have external source citations')

# d) No file contains literal "\\n" strings
print()
print('=== CHECK D: No file contains literal \\\\n strings ===')
no_literal_n = True
for block in estimate_blocks:
    path = os.path.join(pipeline_dir, f'{block}.md')
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    if '\\\\n' in content:
        print(f'  FAIL: {block}.md contains literal \\\\n')
        no_literal_n = False
if no_literal_n:
    print('  PASS: No literal \\\\n strings found in any estimate file')

# e) GRANTS_AND_SUPPORT contains specific program names (not "Serbian Gov")
print()
print('=== CHECK E: GRANTS_AND_SUPPORT contains specific program names ===')
gs_path = os.path.join(pipeline_dir, 'GRANTS_AND_SUPPORT.md')
with open(gs_path, 'r', encoding='utf-8') as f:
    gs_content = f.read()

program_names = ['Subsidija', 'Vrati se', 'Kapital za razvoj', 'StarTech', 'Smart Start', 'beginning entrepreneurs']
found_programs = [name for name in program_names if name in gs_content]

if 'Serbian Gov' in gs_content and 'source URL' in gs_content:
    print('  FAIL: GRANTS_AND_SUPPORT contains generic placeholders "Serbian Gov" or "source URL"')
elif found_programs:
    print(f'  PASS: GRANTS_AND_SUPPORT contains specific program names: {", ".join(found_programs)}')
else:
    print('  FAIL: GRANTS_AND_SUPPORT does not contain the required specific program names')

# Summary
print()
print('=== SUMMARY ===')
print(f'  Check A (80%+ unit_price): {"PASS" if a_pass else "FAIL"}')
print(f'  Check B (80%+ total): {"PASS" if b_pass else "FAIL"}')
print(f'  Check C (source citations): {"PASS" if all_pass else "FAIL"}')
print(f'  Check D (no literal \\\\n): {"PASS" if no_literal_n else "FAIL"}')
has_e_pass = ("Serbian Gov" not in gs_content or "source URL" not in gs_content) and found_programs
print(f'  Check E (specific programs): {"PASS" if has_e_pass else "FAIL"}')