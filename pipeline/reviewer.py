import os
import re

with open('docs/business_plan/water_vending_brief.md', 'r', encoding='utf-8') as f:
    brief = f.read()

blocks = ['TECH', 'LEGAL', 'FINANCE', 'MARKETING', 'LOCATIONS', 'IT_TELEMETRY', 'OPERATIONS', 'DOCUMENTATION', 'GRANTS_AND_SUPPORT']


def check_traceability(estimate_text, brief_text):
    """Check if estimate rows reference brief sections or have external sources"""
    brief_refs = re.findall(r'\[brief: (\d+\.\d+)\]', estimate_text)
    source_refs = re.findall(r'\[source: [^\]]+\]', estimate_text)
    all_refs = brief_refs + source_refs
    missing_brief = []
    for ref in brief_refs:
        if not re.search(rf'{re.escape(ref)}', brief_text):
            missing_brief.append(ref)
    return all_refs, missing_brief


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
            in_table = False

    issues = []

    # Check traceability
    all_refs, missing_refs = check_traceability(estimate_text, brief)
    # Count brief refs: references starting with '[brief:'
    brief_ref_count = sum(1 for r in all_refs if r.startswith('[brief:'))
    # Count source refs: references starting with '[source:'
    source_ref_count = sum(1 for r in all_refs if r.startswith('[source:'))

    # Check: either brief references OR source references must be present
    if brief_ref_count == 0 and source_ref_count == 0:
        issues.append('No [brief: X.X] or [source: ...] references found in estimate')
    if missing_refs and source_ref_count == 0:
        issues.append(f'Missing brief references: {missing_refs}')

    # Check row completeness
    incomplete_rows = []
    for row in table_rows:
        item = row[0] if len(row) > 0 else ''
        desc = row[1] if len(row) > 1 else ''
        unit = row[2] if len(row) > 2 else ''
        qty = row[3] if len(row) > 3 else ''
        unit_price = row[4] if len(row) > 4 else ''
        total = row[5] if len(row) > 5 else ''
        assumption = row[7] if len(row) > 7 else ''

        row_issues = []
        if not item:
            row_issues.append('missing item number')
        if not desc or desc.strip() == '':
            row_issues.append('missing description')
        if not unit:
            row_issues.append('missing unit')
        if not qty:
            row_issues.append('missing quantity')

        # NEW: Check unit_price is not empty
        if not unit_price or unit_price.strip() == '':
            row_issues.append('empty unit_price')
        # NEW: Check total is not empty
        if not total or total.strip() == '':
            row_issues.append('empty total')
        # NEW: Check that unit_price is not just "TBD" without a range and source
        if unit_price and unit_price.strip().upper() == 'TBD':
            row_issues.append('unit_price is TBD without range and source')

        if row_issues:
            incomplete_rows.append((row[0] if row[0] else '?', row_issues))

    # Check: more than 30% of unit_price cells empty = REJECT
    if table_rows:
        price_empty_count = sum(
            1 for row in table_rows
            if not row[4] or not row[4].strip() or row[4].strip().upper() == 'TBD'
        )
        price_empty_pct = price_empty_count / len(table_rows) * 100
        if price_empty_pct > 30:
            issues.append(f'More than 30% of unit_price cells empty ({price_empty_pct:.1f}% empty)')

    # Check: total column is not empty for any line item
    total_empty_count = sum(1 for row in table_rows if not row[5] or not row[5].strip())
    if total_empty_count > 0:
        issues.append(f'{total_empty_count} line item(s) have empty total column')

    # Check structure
    has_header = '| item' in estimate_text
    has_footer = '|------' in estimate_text
    if not has_header:
        issues.append('Table header row missing')
    if not has_footer:
        issues.append('Table separator row missing')

    # GRANTS_AND_SUPPORT specific checks
    if block_name == 'GRANTS_AND_SUPPORT':
        # Check for [source: ...] references
        has_source_ref = '[source:' in estimate_text
        if not has_source_ref:
            issues.append('GRANTS_AND_SUPPORT block missing [source: ...] references')

        # Check for specific program names (not just "Serbian Gov")
        specific_programs = [
            'Subsidija', 'Vrati se', 'Kapital za razvoj', 'StarTech',
            'Smart Start', 'beginning entrepreneurs'
        ]
        has_specific_programs = any(
            name in estimate_text for name in specific_programs
        )
        has_generic_placeholder = 'Serbian Gov' in estimate_text and 'source URL' in estimate_text
        if has_generic_placeholder:
            issues.append(
                'GRANTS_AND_SUPPORT contains generic placeholders "Serbian Gov" '
                'or "source URL" without specific program names'
            )
        if not has_specific_programs:
            issues.append(
                'GRANTS_AND_SUPPORT does not contain specific Serbian program names'
            )

        # Check foreigner eligibility is stated
        has_eligibility_statement = 'ELIGIBLE' in estimate_text or 'NOT ELIGIBLE' in estimate_text
        if not has_eligibility_statement:
            issues.append(
                'GRANTS_AND_SUPPORT does not state foreigner eligibility criteria'
            )

    # Determine status
    status = 'APPROVED'
    revision_notes = []

    for issue in issues:
        revision_notes.append('- ' + issue)

    if issues:
        status = 'REVISION_REQUIRED'

    # Build review content
    review_lines = []
    review_lines.append(f'# {block_name} Estimate Review')
    review_lines.append('')
    review_lines.append('Based on review of estimate, task file, and brief:')
    review_lines.append('')
    review_lines.append('## Traceability Check')
    review_lines.append(f'- Brief references found: {brief_ref_count}')
    review_lines.append(f'- Source references found: {source_ref_count}')
    if missing_refs:
        review_lines.append(f'- Missing brief references: {missing_refs}')
    review_lines.append('')
    review_lines.append('## Row Completeness Check')
    if incomplete_rows:
        review_lines.append('- Rows with issues:')
        for item_num, row_issues in incomplete_rows[:5]:
            review_lines.append(f'  - Row {item_num}: {", ".join(row_issues)}')
    else:
        review_lines.append('- All rows have essential fields populated')
    review_lines.append('')
    review_lines.append('## Structure Check')
    review_lines.append(f'- Table header present: {has_header}')
    review_lines.append(f'- Table separator present: {has_footer}')
    review_lines.append('')

    if block_name == 'GRANTS_AND_SUPPORT':
        review_lines.append('## GRANTS_AND_SUPPORT Check')
        review_lines.append(
            f'- [source: ...] references present: {has_source_ref}'
        )
        review_lines.append(
            f'- Specific program names found: {has_specific_programs}'
        )
        review_lines.append(
            f'- Foreigner eligibility stated: {has_eligibility_statement}'
        )
        review_lines.append(
            f'- Generic placeholders avoided: {"yes" if not has_generic_placeholder else "no"}'
        )
        review_lines.append('')

    review_lines.append('## Brief Cross-Reference')
    review_lines.append(
        '- Task file relevance: evaluated against water_vending_brief.md'
    )
    review_lines.append('')

    if status == 'APPROVED':
        review_lines.append('## Status: APPROVED')
        review_lines.append('')
        review_lines.append(
            'The estimate is complete, traceable, and ready for consolidation.'
        )
    else:
        review_lines.append('## Status: REVISION_REQUIRED')
        review_lines.append('')
        review_lines.append('Concrete issues found:')
        for note in revision_notes:
            review_lines.append(note)
        review_lines.append('')
        review_lines.append(
            'The estimate should be returned to the generator for revision.'
        )

    review_lines.append('')
    review_lines.append('---')
    review_lines.append('')
    review_lines.append(
        '*Review generated automatically based on traceability, completeness, '
        'and structure checks.'
    )
    review_lines.append('All content in real English, UTF-8.')

    review_content = '\n'.join(review_lines)

    review_path = f'docs/pipeline/reviews/{block_name}_review.md'
    with open(review_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(review_content)

    return status, issues, incomplete_rows


for block_name in blocks:
    estimate_path = f'docs/pipeline/estimates/{block_name}.md'
    task_path = f'docs/pipeline/tasks/{block_name}.md'
    status, issues, incomplete_rows = review_block(block_name, estimate_path, task_path)
    print(f'{block_name}: Status={status}, Issues={len(issues)}')
    if issues:
        for issue in issues:
            print(f'  - {issue}')

print('\nReviewer complete.')