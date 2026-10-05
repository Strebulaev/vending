import re
import os

with open('water_vending_brief.md', 'r', encoding='utf-8') as f:
    brief = f.read()

print("Brief loaded, length:", len(brief))

block_keywords = {
    'TECH': ['Low cost', 'Repairability', 'Serviceability', 'Observability', 'Integration',
             'coin acceptor', 'bill acceptor', 'cashless', 'Payment modules', 'Camera',
             'GPS tracker', 'Telemetry', 'Heater', 'Assembly', 'Production',
             'Coordination', 'Tolerances', 'Anti-vandalism',
             '2.1', '2.2', '2.3', '2.4'],
    'GRANTS_AND_SUPPORT': ['Grants', 'Subsidies', 'Support', 'Serbian', 'foreign', 'foreign-owned'],
}

blocks = ['TECH', 'LEGAL', 'FINANCE', 'MARKETING', 'LOCATIONS', 'IT_TELEMETRY', 'OPERATIONS', 'DOCUMENTATION', 'GRANTS_AND_SUPPORT']

for block_name in blocks:
    task_path = f'pipeline/tasks/{block_name}.md'
    with open(task_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(f'# {block_name} Block Task\n\n')
        if block_name == 'GRANTS_AND_SUPPORT':
            f.write('### Serbian Government Grants, Subsidies, and Support Programs\n')
            f.write('- Research Serbian government grant programs available to foreigners and foreign-owned businesses\n')
            f.write('- Identify eligibility criteria, application status, and amounts (RSD + approximate EUR)\n')
            f.write('- Document beneficiary type, program name (Latin + English translation), body, source URL\n')
            f.write('- Cover subsidies and support programs relevant to water vending machine projects\n')
        else:
            f.write('### Key areas from brief:\n')
            kw_covered = set()
            for line in brief.split('\n'):
                line_stripped = line.strip()
                for kw in block_keywords.get(block_name, []):
                    if kw.lower() in line_stripped.lower() and kw not in kw_covered:
                        f.write('- ' + line_stripped + '\n')
                        kw_covered.add(kw)
            if not kw_covered:
                f.write('_No specific keywords matched from brief_\n')
        f.write('\n### Action items:\n')
        f.write('- Identify and catalog all relevant items from the brief\n')
        f.write('- Determine data gaps and mark as TBD where needed\n')
        f.write('- Prepare for cost estimate generation\n')
    print('Created', task_path)

print('\nRouter complete. All task files written.')