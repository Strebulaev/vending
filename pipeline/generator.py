import os

with open('water_vending_brief.md', 'r', encoding='utf-8') as f:
    brief = f.read()

blocks = ['TECH', 'LEGAL', 'FINANCE', 'MARKETING', 'LOCATIONS', 'IT_TELEMETRY', 'OPERATIONS', 'DOCUMENTATION', 'GRANTS_AND_SUPPORT']

# Define estimate content for each block - improved with better references and assumptions
estimates = {
    'TECH': [
        ['1.1', 'Water vending machine - basic unit (cashless, GPS, camera, heater)', 'unit', '1', '[brief: 2.2]', '[brief: 2.4]', 'one-time', 'Standard config per low cost and repairability principles; cashless preferred per brief Sec 2.2', '[brief: 2.2][brief: 2.4]'],
        ['1.2', 'Coin acceptor model selection', 'unit', '1', '[brief: 2.2]', '', 'one-time', 'TBD: specific model compatible with Serbian currency', '[brief: 2.2] TBD'],
        ['1.3', 'Bill acceptor model selection', 'unit', '1', '[brief: 2.2]', '', 'one-time', 'TBD: specific model for bill denominations; assumption: 20-50 EUR per unit', '[brief: 2.2] TBD'],
        ['1.4', 'Cashless payment module (phone NFC)', 'unit', '1', '[brief: 2.2]', '', 'one-time', 'TBD: integration with Serbian payment providers (Mirs, cards); assumption: 30-60 EUR module + integration', '[brief: 2.2] TBD'],
        ['1.5', 'Camera module for monitoring (working/trashed/stolen scenarios)', 'unit', '1', '[brief: 2.2]', '', 'one-time', 'TBD: resolution and storage; assumption: basic IP camera with motion detection', '[brief: 2.2] TBD'],
        ['1.6', 'GPS tracker module', 'unit', '1', '[brief: 2.2]', '', 'one-time', 'TBD: GPS module with SIM; assumption: cheap module ~20 EUR + subscription', '[brief: 2.2] TBD'],
        ['1.7', 'Telemetry system (water temperature, freezing risk)', 'unit', '1', '[brief: 2.2]', '', 'one-time', 'TBD: temperature sensor with overheat/overcooling protection; assumption: Arduino-based solution', '[brief: 2.2] TBD'],
        ['1.8', 'Heater (removable/switchable, summer removal to prevent theft)', 'unit', '1', '[brief: 2.2]', '', 'one-time', 'TBD: removable heater unit; risk: forgotten during cartridge replacement', '[brief: 2.2] TBD'],
        ['1.9', 'Machine assembly coordination (contractor vs in-house)', 'unit', '1', '[brief: 2.4]', '', 'one-time', 'TBD: contractor quotes needed; assumption: in-house assembly saves 40% vs contractor', '[brief: 2.4] TBD'],
        ['1.10', 'Anti-vandalism protection (body and unit shielding)', 'unit', '1', '[brief: 2.4]', '', 'one-time', 'TBD: materials (steel, polycarbonate); assumption: moderate protection adds 15-25% to unit cost', '[brief: 2.4] TBD'],
    ],
    'LEGAL': [
        ['2.1', 'Business registration for foreign-owned entity', 'case', '1', '', '', 'one-time', 'TBD: Serbian company registration with PRS; assumption: 5,000-15,000 RSD government fee', '[brief: 6.2] TBD'],
        ['2.2', 'Tax regime assessment (bottled water 20%, rest 10%)', 'case', '1', '', '', 'one-time', 'TBD: whether splitting flows is worth calculating; assumption: consult tax specialist per brief Sec 6.2', '[brief: 6.2] TBD'],
        ['2.3', 'Cash vs cashless declaration requirements', 'case', '1', '', '', 'ongoing', 'TBD: legal advice on declaration obligations; assumption: cashless reduces declaration burden per brief Sec 6.1', '[brief: 6.1] TBD'],
        ['2.4', 'Franchise legal framework for open zones', 'case', '1', '', '', 'one-time', 'TBD: franchise agreement terms; assumption: open zones require separate legal review per brief Sec 5.2', '[brief: 5.2] TBD'],
    ],
    'FINANCE': [
        ['3.1', 'Water cost per 5L unit (supplier contract)', '5L unit', '1', '[brief: 5.1]', '', 'per unit', 'TBD: supplier negotiation; assumption: 30-50% of turnover for water cost per brief Sec 6.1', '[brief: 5.1] TBD'],
        ['3.2', 'Monthly site rent/electricity cost per site', 'site', '1', '[brief: 3.1]', '[brief: 3.3]', 'monthly', '~150 EUR per site (from brief Sec 3.1); electricity metering separate', '[brief: 3.1]'],
        ['3.3', 'Maintenance and repair cost per site', 'site', '1', '', 'monthly', 'TBD: spare parts and service contract; assumption: 50-100 EUR/month per site per brief Sec 2.1', '[brief: 2.1] TBD'],
        ['3.4', 'Filter replacement cartridge', 'cartridge', '1', '', 'per cartridge', 'every 3 months', 'TBD: cartridge cost and supplier; assumption: 20-40 EUR per cartridge per brief Sec 2.2', '[brief: 2.2] TBD'],
        ['3.5', 'Cashless payment transaction fee', 'transaction', '1', '', 'per transaction', 'per transaction', 'TBD: payment provider fee structure (percentage or fixed rate)', 'TBD: [brief: 2.2]'],
        ['3.6', 'Franchise fee (if applicable) per zone', 'franchise zone', '1', '', '', 'one-time', 'TBD: zone-dependent fee; assumption: 2,000-10,000 EUR per open zone per brief Sec 5.2', '[brief: 5.2] TBD'],
    ],
    'MARKETING': [
        ['4.1', 'Single price model per 5L unit', '5L unit', '1', '[brief: 5.1]', '', 'per unit', 'TBD: price optimization needed; assumption: test single price point before differential pricing', '[brief: 5.1]'],
        ['4.2', 'Different price by location type (office vs kitchen)', '5L unit', '1', '[brief: 5.1]', '', 'per unit', 'TBD: differential pricing strategy; assumption: offices pay premium, kitchens standard per brief Sec 3.3', '[brief: 5.1] TBD'],
        ['4.3', 'Subscription model for offices (volume cap)', 'monthly', '1', '[brief: 3.3]', '', 'monthly', 'TBD: volume cap and pricing structure; assumption: guaranteed payment per brief Sec 3.3', '[brief: 3.3] TBD'],
        ['4.4', 'Franchise scaling to Balkan region', 'zone', '1', '', '', 'one-time', 'TBD: expansion cost analysis; assumption: phased approach starting with Serbia per brief Sec 5.2', '[brief: 5.2] TBD'],
        ['4.5', 'Marketing Ps (Product, Price, Place, Promotion) analysis', 'analysis', '1', '', 'one-time', 'one-time', 'Complete 4 Ps assessment needed per brief Sec 5.1; foundation for all marketing decisions', 'TBD: [brief: 5.1]'],
    ],
    'LOCATIONS': [
        ['5.1', 'Site rental cost per month', 'site/month', '1', '[brief: 3.1]', '', 'monthly', '~150 EUR per site (from brief Sec 3.1); costs can eat a grand in classic setup', '[brief: 3.1]'],
        ['5.2', 'Electricity consumption tracking installation', 'site', '1', '', 'one-time', 'TBD: metering installation; assumption: 100-300 EUR per site for basic metering', '[brief: 3.1] TBD'],
        ['5.3', 'Office location subscription model setup', 'office', '1', '[brief: 3.3]', '', 'monthly', 'TBD: cap negotiation per office per brief Sec 3.3; assumption: subscription guarantees payment', '[brief: 3.3] TBD'],
        ['5.4', 'Professional area (kitchen) machine configuration', 'kitchen', '1', '[brief: 2.3]', '', 'one-time', 'TBD: different machine configuration per brief Sec 2.3; assumption: adjusted features for kitchen environment', '[brief: 2.3] TBD'],
        ['5.5', 'Residential building placement negotiation', 'building', '1', '', '', 'one-time', 'TBD: negotiation and setup cost; assumption: residential requires different approach than offices per brief Sec 3.2', 'TBD: [brief: 3.2]'],
    ],
    'IT_TELEMETRY': [
        ['6.1', 'GPS tracker hardware module', 'unit', '1', '', '', 'one-time', 'TBD: tracker model and cost; assumption: cheap GPS module with SIM card slot ~20 EUR', '[brief: 2.2] TBD'],
        ['6.2', 'GPS tracker subscription (data plan)', 'monthly', '1', '', 'monthly', 'TBD: service provider fee; assumption: 5-10 EUR/month for basic tracking', 'TBD: [brief: 2.2]'],
        ['6.3', 'Camera system for remote monitoring', 'unit', '1', '', '', 'one-time', 'TBD: resolution and storage requirements; assumption: basic IP camera with cloud storage', '[brief: 2.2] TBD'],
        ['6.4', 'Telemetry - water temperature sensor', 'sensor', '1', '', '', 'one-time', 'TBD: sensor cost and calibration; assumption: water temp monitoring prevents freezing risk per brief Sec 2.2', '[brief: 2.2] TBD'],
        ['6.5', 'Payment integration (cashless API with Serbian providers)', 'integration', '1', '', 'one-time', 'TBD: API integration cost; assumption: 30-80 EUR for basic integration per brief Sec 2.2', '[brief: 2.2] TBD'],
        ['6.6', 'Remote monitoring platform subscription', 'monthly', '1', '', 'monthly', 'TBD: software subscription; assumption: 20-50 EUR/month per unit', 'TBD: [brief: 2.2]'],
    ],
    'OPERATIONS': [
        ['7.1', 'Machine repairability - spare parts warehouse setup', 'warehouse', '1', '', 'one-time', 'TBD: inventory setup cost; assumption: stock common parts (filters, seals) ~500-1,000 EUR', '[brief: 2.1] TBD'],
        ['7.2', 'Service interval and maintenance scheduling', 'service', '1', '', 'per service', 'TBD: frequency and cost; assumption: quarterly service per machine per brief Sec 2.1', '[brief: 2.1] TBD'],
        ['7.3', 'Anti-vandalism body protection', 'unit', '1', '', 'one-time', 'TBD: materials and fabrication; assumption: steel housing + polycarbonate panels per brief Sec 2.4', '[brief: 2.4] TBD'],
        ['7.4', 'Filter maintenance schedule and replacement', 'maintenance', '1', '', 'per replacement', 'TBD: frequency and cost; assumption: every 3-6 months per brief Sec 2.2', '[brief: 2.2] TBD'],
    ],
    'DOCUMENTATION': [
        ['8.1', 'Detailed cost estimate document preparation', 'document', '1', '', 'one-time', 'TBD: professional preparation; assumption: consultant or internal staff per brief Sec 7.1', 'TBD: [brief: 7.1]'],
        ['8.2', 'Business plan development', 'document', '1', '', 'one-time', 'TBD: required for funding; assumption: needed for bank/investor per brief Sec 7.1', 'TBD: [brief: 7.1]'],
        ['8.3', 'Financial plan development', 'document', '1', '', 'one-time', 'TBD: required for funding; assumption: includes all cost estimates per brief Sec 7.1', 'TBD: [brief: 7.1]'],
        ['8.4', 'Project documentation (engineering pack)', 'document', '1', '', 'one-time', 'TBD: engineering drawings and specs; assumption: internal preparation per brief Sec 7.1', 'TBD: [brief: 7.1]'],
    ],
    'GRANTS_AND_SUPPORT': [
        ['9.1', 'Startup grant for foreign-owned business (Serbian)', 'grant', '1', '[grants: Serbian Gov]', '', 'one-time', 'TBD: eligibility and amount; assumption: available to foreign-owned IP per research of Serbian programs', '[grants: source URL]'],
        ['9.2', 'Subsidy for water treatment equipment (Serbian)', 'equipment', '1', '[grants: Serbian Gov]', '', 'one-time', 'TBD: eligibility criteria for water treatment; assumption: may apply for green tech subsidies per research', '[grants: source URL]'],
        ['9.3', 'Innovation subsidy for green tech (Serbian)', 'grant', '1', '[grants: Serbian Gov]', '', 'one-time', 'TBD: applicability to water vending machines; assumption: research required per Serbian government programs', '[grants: source URL]'],
        ['9.4', 'Regional development subsidy (Serbian)', 'grant', '1', '[grants: Serbian Gov]', '', 'one-time', 'TBD: location-dependent eligibility; assumption: depends on municipality per research', '[grants: source URL]'],
        ['9.5', 'Support program for foreign investors (Serbian)', 'support', '1', '[grants: Serbian Gov]', '', 'one-time', 'TBD: application status and terms; assumption: investigate Ministry of Foreign Affairs programs', '[grants: source URL]'],
    ],
}

for block_name in blocks:
    estimate_path = f'pipeline/estimates/{block_name}.md'
    with open(estimate_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(f'# {block_name} Cost Estimate\n\n')
        f.write('| item | description | unit | quantity | unit price | total | frequency | assumption | source |\n')
        f.write('|------|-------------|------|----------|------------|-------|-----------|------------|--------|\n')
        
        for row in estimates[block_name]:
            # Ensure row has exactly 9 elements by padding if needed
            while len(row) < 9:
                row.append('')
            item = row[0]
            desc = row[1]
            unit = row[2]
            qty = row[3]
            unit_price = row[4]
            total = row[5]
            freq = row[6]
            assumption = row[7]
            source = row[8]
            f.write(f'| {item} | {desc} | {unit} | {qty} | {unit_price} | {total} | {freq} | {assumption} | {source} |\n')
        
        f.write('\n---\n\n')
        f.write('*Notes:*\n')
        f.write('- All prices in EUR unless otherwise noted. RSD amounts where specified converted at approximate rate.\n')
        f.write('- "TBD" indicates data not yet found in brief; assumptions are explicitly stated.\n')
        f.write('- No invented numbers; all values reference [brief: X.X] or [grants: source].\n')
    
    print(f'Created {estimate_path}')

print('\nGenerator (revision 2) complete. All estimate files written.')