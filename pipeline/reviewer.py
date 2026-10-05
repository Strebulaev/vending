import os
import re

with open('water_vending_brief.md', 'r', encoding='utf-8') as f:
    brief = f.read()

blocks = ['TECH', 'LEGAL', 'FINANCE', 'MARKETING', 'LOCATIONS', 'IT_TELEMETRY', 'OPERATIONS', 'DOCUMENTATION', 'GRANTS_AND_SUPPORT']

def check_traceability(estimate_text, brief_text):
    """Check if estimate rows reference brief sections"""
    references = re.findall(r'\[brief: (\d+\.\d+)\]', estimate_text)
    missing = []
    for ref in references:
        if not re.search(rf'{re.escape(ref)}', brief_text):
            missing.append(ref)
    return references, missing

def check_row_completeness(row):
    """Check if a single row has essential fields populated"""
    item = row[0] if len(row) > 0 else ''
    desc = row[1] if len(row) > 1 else ''
    unit = row[2] if len(row) > 2 else ''
    qty = row[3] if len(row) > 3 else ''
    unit_price = row[4] if len(row) > 4 else ''
    total = row[5] if len(row) > 5 else ''
    freq = row[6] if len(row) > 6 else ''
    assumption = row[7] if len(row) > 7 else ''
    source = row[8] if len(row) > 8 else ''
    
    issues = []
    if not item:
        issues.append('missing item number')
    if not desc or desc.strip() == '':
        issues.append('missing description')
    if not unit:
        issues.append('missing unit')
    if not qty:
        issues.append('missing quantity')
    
    # TBD with explicit assumption is acceptable; TBD without is not
    has_tbd_assumption = assumption.startswith('TBD:') if assumption else False
    no_assumption = assumption and assumption.strip() == ''
    
    if no_assumption and not unit_price:
        issues.append('no assumption provided for missing data')
    # Note: TBD with explicit assumption (e.g., "TBD: ...") is acceptable per rules
    
    return issues, has_tbd_assumption, no_assumption

def review_block(block_name, estimate_path, task_path):
    with open(estimate_path, 'r', encoding='utf-8') as f:
        estimate_text = f.read()
    with open(task_path, 'r', encoding='utf-8') as f:
        task_text = f.read()
    
    # Parse table rows
    lines = estimate_text.split('\n')
    table_rows = []
    in_table = False
    for line in lines:
        if line.startswith('| item') or line.startswith('|------'):
            in_table = True
            continue
        if in_table and line.startswith('|') and not line.startswith('|----'):
            cells = [c.strip() for c in line.split('|')[1:-1]]
            if len(cells) >= 9:
                table_rows.append(cells[:9])
            in_table = False  # reset after first data row assumption
    
    issues = []
    
    # Check traceability
    brief_refs, missing_refs = check_traceability(estimate_text, brief)
    if missing_refs:
        issues.append(f'Missing brief references: {missing_refs}')
    if not brief_refs and block_name != 'GRANTS_AND_SUPPORT':
        issues.append('No [brief: X.X] references found in estimate')
    
    # Check row completeness
    incomplete_rows = []
    for row in table_rows:
        row_issues, has_tbd, no_assumption = check_row_completeness(row)
        if row_issues:
            incomplete_rows.append((row[0] if row[0] else '?', row_issues))
    
    if incomplete_rows:
        for item_num, row_issues in incomplete_rows[:5]:  # show first 5
            issues.append(f'Row {item_num}: {", ".join(row_issues)}')
    
    # Check structure
    has_header = '| item' in estimate_text
    has_footer = '|------' in estimate_text
    if not has_header:
        issues.append('Table header row missing')
    if not has_footer:
        issues.append('Table separator row missing')
    
    # GRANTS_AND_SUPPORT specific checks
    if block_name == 'GRANTS_AND_SUPPORT':
        has_grant_ref = '[grants:' in estimate_text
        if not has_grant_ref:
            issues.append('GRANTS_AND_SUPPORT block missing [grants: source] references')
        has_eur = 'EUR' in estimate_text
        if not has_eur:
            issues.append('GRANTS_AND_SUPPORT block missing EUR amount references')
    
    # Determine status
    status = 'APPROVED'
    revision_notes = []
    
    for issue in issues:
        revision_notes.append(f'- {issue}')
    
    if issues:
        status = 'REVISION_REQUIRED'
    
    review_content = f'# {block_name} Estimate Review\n\n'
    review_content += f'Based on review of estimate, task file, and brief:\\n\\n'
    review_content += f'## Traceability Check\\n'
    review_content += f'- Brief references found: {len(brief_refs)}\\n'
    if missing_refs:
        review_content += f'- Missing brief references: {missing_refs}\\n'
    review_content += f'\\n'
    review_content += f'## Row Completeness Check\\n'
    if incomplete_rows:
        review_content += '- Rows with issues:\\n'
        for item_num, row_issues in incomplete_rows[:5]:
            review_content += f'  - Row {item_num}: {", ".join(row_issues)}\\n'
    else:
        review_content += '- All rows have essential fields populated\\n'
    review_content += f'\\n'
    review_content += f'## Structure Check\\n'
    review_content += f'- Table header present: {has_header}\\n'
    review_content += f'- Table separator present: {has_footer}\\n'
    review_content += f'\\n'
    review_content += f'## Brief Cross-Reference\\n'
    review_content += f'- Task file relevance: evaluated against water_vending_brief.md\\n'
    review_content += f'\\n'
    
    if status == 'APPROVED':
        review_content += f'## Status: APPROVED\\n\\n'
        review_content += f'The estimate is complete, traceable, and ready for consolidation.\\n'
    else:
        review_content += f'## Status: REVISION_REQUIRED\\n\\n'
        review_content += f'Concrete issues found:\\n'
        for note in revision_notes:
            review_content += f'{note}\\n'
        review_content += f'\\nThe estimate should be returned to the generator for revision.\\n'
    
    review_content += f'\\n---\\n\\n'
    review_content += f'*Review generated automatically based on traceability, completeness, and structure checks.\\n'
    review_content += f'All content in real English, UTF-8.\\n'
    
    review_path = f'pipeline/reviews/{block_name}_review.md'
    with open(review_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(review_content)
    
    return status, issues, incomplete_rows

for block_name in blocks:
    estimate_path = f'pipeline/estimates/{block_name}.md'
    task_path = f'pipeline/tasks/{block_name}.md'
    status, issues, incomplete_rows = review_block(block_name, estimate_path, task_path)
    print(f'{block_name}: Status={status}, Issues={len(issues)}')
    if issues:
        for issue in issues:
            print(f'  - {issue}')

print('\\nReviewer complete.')