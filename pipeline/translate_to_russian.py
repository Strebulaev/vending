import os
import re

def translate_to_russian(text):
    """Translate English text to Russian, preserving table structure and references."""
    
    lines = text.split('\n')
    result_lines = []
    
    in_table = False
    
    for line in lines:
        # Check if this is a table row (starts with | and has content)
        if re.match(r'^\|', line):
            in_table = True
            result_lines.append(line)
            continue
        
        # If we were in a table and hit a non-table line, exit table mode
        if in_table and not re.match(r'^\|', line):
            in_table = False
        
        if in_table:
            # Inside table - keep line as-is to preserve structure
            result_lines.append(line)
            continue
        
        # Non-table line - translate it
        translated = translate_line(line)
        result_lines.append(translated)
    
    return '\n'.join(result_lines)


def translate_line(line):
    """Translate a single line of English text to Russian."""
    
    # Preserve [brief: X.X] and [grants: source] references
    # Preserve EUR, RSD markers, TBD markers
    
    # Find and preserve references first
    brief_refs = re.findall(r'\[brief: \d+\.\d+\]', line)
    grants_refs = re.findall(r'\[grants: [^\]]+\]', line)
    tdbs = re.findall(r'\bTBD\b', line)
    eur_patterns = re.findall(r'\bEUR\b', line)
    rsd_patterns = re.findall(r'\bРСД\b', line)
    
    # Remove references temporarily for translation
    temp = line
    for ref in brief_refs:
        temp = temp.replace(ref, ' [BRIEF_REF] ')
    for ref in grants_refs:
        temp = temp.replace(ref, ' [GRANTS_REF] ')
    for tdb in tdbs:
        temp = temp.replace(tdb, ' [TBD] ')
    for eur in eur_patterns:
        temp = temp.replace(eur, ' [EUR] ')
    for rsd in rsd_patterns:
        temp = temp.replace(rsd, ' [РСД] ')
    
    # Comprehensive translation map
    translation_map = {
        # Header/section titles
        'Consolidated Cost Estimate Summary': 'Сводная стоимостная оценка',
        'Water Vending Project - Initial Cost Estimate by Blocks': 'Водопроизводительный проект - Первоначальная стоимостная оценка по блокам',
        'Based on: water_vending_brief.md': 'Основано на: water_vending_brief.md',
        'Total blocks: 9': 'Всего блоков: 9',
        'Total estimate items across all blocks: 49': 'Общая стоимость по всем блокам: 49',
        '*All values reference [brief: X.X] or [grants: source]. TBD entries have explicit assumptions. No invented numbers.': \
            '*Все значения ссылаются на [brief: X.X] или [grants: source]. Строки с TBD имеют явные предположения. Выдуманные числа не допускаются.',
        
        # Summary section block headers
        '## TECH': '## ТЕХ',
        '## LEGAL': '## ЛЕГАЛ',
        '## FINANCE': '## ФИНАНСЫ',
        '## MARKETING': '## МАРКЕТИНГ',
        '## LOCATIONS': '## ЛОКАЦИИ',
        '## IT_TELEMETRY': '## IT ТЕЛЕМЕТРИЯ',
        '## OPERATIONS': '## ОПЕРАЦИИ',
        '## DOCUMENTATION': '## ДОКУМЕНТИРОВАНИЕ',
        '## GRANTS_AND_SUPPORT': '## ГРАНТЫ И ПОДДЕРЖКА',
        
        # Frequency distributions
        'one-time': 'разово',
        'monthly': 'месяц',
        'per unit': 'на единицу',
        'per transaction': 'на транзакцию',
        'every 3 months': 'каждые 3 месяца',
        'TBD': 'TBD',
        
        # Notes
        'All prices in EUR unless otherwise noted. RSD amounts where specified converted at approximate rate.': \
            'Все цены в EUR, если иное не указано. Суммы в РСД, указанные где-то, конвертируются по приблизительному курсу.',
        'No invented numbers; all values reference [brief: X.X] or [grants: source].': \
            'Выдуманные числа не допускаются; все значения ссылаются на [brief: X.X] или [grants: source].',
        
        # assumptions.md specific
        'All assumptions from cost estimate blocks:': 'Все предположения из стоимостных оценок:',
        'Based on: water_vending_brief.md': 'Основано на: water_vending_brief.md',
        
        # General phrases that appear in files
        'Water Vending Project': 'Водопроизводительный проект',
        'Project Context': 'Контекст проекта',
        'Machine Requirements': 'Требования к машине',
        'General Principles': 'Общие принципы',
        'Low cost': 'Низкая стоимость',
        'Repairability': 'Ремонопригодность',
        'Serviceability': 'Обслуживаемость',
        'Observability': 'Обнаруживаемость',
        'Integration': 'Интеграция',
        'Payment modules': 'Модули оплаты',
        'Coin acceptor': 'Прием монет',
        'Bill acceptor': 'Прием купюр',
        'Cashless': 'Безналичный',
        'Camera': 'Камера',
        'GPS tracker': 'GPS трекер',
        'Telemetry': 'Тelemетр',
        'Heater': 'Обогреватель',
        'Production and Assembly': 'Производство и монтаж',
        'Anti-vandalism': 'Антивандальная защита',
        'Site Requirements': 'Требования к сайту',
        'Target Audiences': 'Целевые аудитории',
        'Entry Scenarios': 'Сценarios входa',
        'Product (Water)': 'Продукт (Вода)',
        'Pricing and Franchise': 'Цены и франшиза',
        'Cash': 'Наличные',
        'Tax Aspect': 'Налоговый аспект',
        'Documentation and Planning': 'Документация и планирование',
        'What Is Needed': 'Что нужно',
        'Process': 'Процесс',
        'Open Questions': 'Открытые вопросы',
        'Next Steps': 'Следующие шаги',
        
        # New phrases for consolidated files
        '### Total rows:': '### Всего строк:',
        '### Frequency distribution:': '### Частотное распределение:',
        '### TBD assumptions:': '### Предположения TBD:',
        '### TBD unit prices:': '### Цены TBD:',
        '*All prices in EUR unless otherwise noted.': \
            '*Все цены в EUR, если иное не указано.',
        '- "TBD" indicates data not yet found in brief; assumptions are explicitly stated.': \
            '- "TBD" указывает на данные, не найденные в брифе; предположения делаются явными.',
        '- No invented numbers; all values reference [brief: X.X] or [grants: source].': \
            '- Выдуманные числа не допускаются; все значения ссылаются на [brief: X.X] или [grants: source].',
    }
    
    # Apply translations
    for eng, rus in translation_map.items():
        if eng in temp:
            temp = temp.replace(eng, rus)
    
    # Restore references
    temp = temp.replace(' [BRIEF_REF]', '')
    for ref in brief_refs:
        temp = temp.replace(' [BRIEF_REF]', ref, 1)
    for ref in grants_refs:
        temp = temp.replace(' [GRANTS_REF]', ref, 1)
    for tdb in tdbs:
        temp = temp.replace(' [TBD]', tdb, 1)
    for eur in eur_patterns:
        temp = temp.replace(' [EUR]', eur, 1)
    for rsd in rsd_patterns:
        temp = temp.replace(' [РСД]', rsd, 1)
    
    # Clean up double spaces
    temp = re.sub(r'  +', ' ', temp)
    
    return temp


def process_file(input_path, output_path):
    """Process a single file: read, translate, write."""
    
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Translate the content
    translated = translate_to_russian(content)
    
    # Write the translated file
    with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(translated)
    
    print(f'Processed: {input_path} -> {output_path}')


# Main processing
consolidated_dir = 'pipeline/consolidated'
ru_dir = 'pipeline/consolidated_ru'

# Get all .md files from consolidated
files = []
for f in sorted(os.listdir(consolidated_dir)):
    if f.endswith('.md'):
        files.append(f)

print(f'Found {len(files)} files to translate\\n')

for fname in files:
    input_path = os.path.join(consolidated_dir, fname)
    output_path = os.path.join(ru_dir, fname)
    process_file(input_path, output_path)

print('\\nAll files processed.')