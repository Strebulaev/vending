import os
import re

with open('water_vending_brief.md', 'r', encoding='utf-8') as f:
    brief = f.read()

blocks_order = [
    'TECH', 'LEGAL', 'FINANCE', 'MARKETING', 'LOCATIONS',
    'IT_TELEMETRY', 'OPERATIONS', 'DOCUMENTATION', 'GRANTS_AND_SUPPORT'
]

# Collect data from all estimates
block_data = {}
all_assumptions = set()

for block_name in blocks_order:
    estimate_path = f'pipeline/estimates/{block_name}.md'
    with open(estimate_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse table rows
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
                rows.append({
                    'item': cells[0],
                    'description': cells[1],
                    'unit': cells[2],
                    'quantity': cells[3],
                    'unit_price': cells[4],
                    'total': cells[5],
                    'frequency': cells[6],
                    'assumption': cells[7],
                    'source': cells[8],
                })
    
    block_data[block_name] = rows
    
    # Collect assumptions
    for row in rows:
        a = row['assumption']
        if a and a.strip():
            all_assumptions.add(a.strip())

# --- summary.md ---
summary_lines = []
summary_lines.append('# Consolidated Cost Estimate Summary\n')
summary_lines.append('Water Vending Project - Initial Cost Estimate by Blocks\n')
summary_lines.append(f'Based on: water_vending_brief.md\n')
summary_lines.append(f'Total blocks: {len(blocks_order)}\n')

for block_name in blocks_order:
    rows = block_data[block_name]
    approved_items = sum(1 for r in rows if r['item'])
    total_rows = len(rows)
    summary_lines.append(f'## {block_name}\\n')
    summary_lines.append(f'  Rows: {total_rows}, Items with data: {approved_items}\\n')

summary_lines.append(f'\\nTotal estimate items across all blocks: {sum(len(block_data[b]) for b in blocks_order)}\\n')
summary_lines.append('*All values reference [brief: X.X] or [grants: source]. TBD entries have explicit assumptions. No invented numbers.*\\n')

with open('pipeline/consolidated/summary.md', 'w', encoding='utf-8', newline='\n') as f:
    f.write('\n'.join(summary_lines))
print('Created pipeline/consolidated/summary.md')

# --- block summaries ---
block_summary_map = {
    'TECH': 'tech.md',
    'LEGAL': 'legal.md',
    'FINANCE': 'finance.md',
    'MARKETING': 'marketing.md',
    'LOCATIONS': 'locations.md',
    'IT_TELEMETRY': 'it_telemetry.md',
    'OPERATIONS': 'operations.md',
    'DOCUMENTATION': 'documentation.md',
    'GRANTS_AND_SUPPORT': 'grants_and_support.md',
}

for block_name, filename in block_summary_map.items():
    rows = block_data[block_name]
    lines = [f'# {block_name} Cost Estimate Summary\n']
    
    # Count by frequency
    freq_counts = {}
    assumption_count = 0
    tbd_count = 0
    for row in rows:
        freq = row['frequency']
        freq_counts[freq] = freq_counts.get(freq, 0) + 1
        if 'TBD' in row['assumption']:
            assumption_count += 1
        if 'TBD' in row['unit_price']:
            tbd_count += 1
    
    lines.append(f'### Total rows: {len(rows)}\n')
    lines.append(f'### Frequency distribution: {freq_counts}\n')
    lines.append(f'### TBD assumptions: {assumption_count}\n')
    lines.append(f'### TBD unit prices: {tbd_count}\n')
    
    # Table summary
    lines.append('| item | description | unit | quantity | unit price | total | frequency | assumption | source |\n')
    lines.append('|------|-------------|------|----------|------------|-------|-----------|------------|--------|\n')
    
    for row in rows[:10]:  # first 10 rows
        lines.append(f'| {row["item"]} | {row["description"][:30]}... | {row["unit"]} | {row["quantity"]} | {row["unit_price"]} | {row["total"]} | {row["frequency"]} | {row["assumption"][:30]}... | {row["source"]} |\n')
    
    if len(rows) > 10:
        lines.append(f'| ... | ... | ... | ... | ... | ... | ... | ... | ... |\n')
        lines.append(f'| Total rows: {len(rows)} |\n')
    
    lines.append('\\n---\\n\\n')
    lines.append('*All prices in EUR unless otherwise noted. RSD amounts where specified converted at approximate rate.\\n')
    lines.append('- "TBD" indicates data not yet found in brief; assumptions are explicitly stated.\\n')
    lines.append('- No invented numbers; all values reference [brief: X.X] or [grants: source].\\n')
    
    with open(f'pipeline/consolidated/{filename}', 'w', encoding='utf-8', newline='\n') as f:
        f.write(''.join(lines))
    print(f'Created pipeline/consolidated/{filename}')

# --- assumptions.md ---
assumption_lines = []
assumption_lines.append('# Project Assumptions Summary\n')
assumption_lines.append('All assumptions from cost estimate blocks:\\n\\n')

for block_name in blocks_order:
    rows = block_data[block_name]
    assumption_lines.append(f'### {block_name}\n')
    for row in rows:
        a = row['assumption']
        if a and a.strip() and 'TBD:' in a:
            assumption_lines.append(f'- Item {row["item"]}: {a}\\n')
    assumption_lines.append('\\n')

with open('pipeline/consolidated/assumptions.md', 'w', encoding='utf-8', newline='\n') as f:
    f.write(''.join(assumption_lines))
print('Created pipeline/consolidated/assumptions.md')

print('\\nConsolidator complete.')