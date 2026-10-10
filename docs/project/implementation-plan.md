# Water Vending Machine Project — Business Idea Summary

> **Note 2026-10-08 (owner rule: invented figures are not written; unknown is written as 'not found').** This plan was machine-drafted from the brief. The brief contains only illustrative remarks (a site example of about 150 EUR per month, water cost 30-50% of turnover, the 20%/10% split, the 2 L example), which are not facts. All module prices, ranges and week numbers of the earlier draft were removed: unknown values read 'not found' and are listed in `docs/reports/unknowns-and-open-issues.md`. Phases are an order of work, not a schedule; for lead times see `docs/certification/costs-and-timeline.md` and `docs/facts/0031-freight-rates-china-serbia.md`. The pilot scope is one residential machine (decisions 0003, 0011); phases 3-6 contain deferred office/kitchen/franchise work.

## What
A network of drinking water vending machines that provide purified, drinkable water through a cashless payment system (phone NFC → purchase 5L water). The machines are designed for low cost, repairability, serviceability, and remote observability. Target locations include offices, professional areas (kitchens), and selected residential buildings in Serbia and the Balkan region.

## How
1. **Legal foundation**: Register a foreign-owned entity in Serbia, determine tax regime (the brief mentions 20% for bottled water and 10% for other products; unconfirmed, fact 0002), and apply for available government grants/subsidies for foreign investors and water treatment equipment.
2. **Machine design**: Build/assemble a water vending machine with cashless payment (priority), coin/bill acceptors (optional), camera for state monitoring, GPS tracker, telemetry (water temperature control), and removable heater (summer removal to prevent theft). Anti-vandalism protection via steel/polycarbonate construction.
3. **Location strategy**: Negotiate site rentals (price: not found) near the business own usage area. Install electricity metering. Target offices (subscription model with volume cap), professional kitchens (different machine config), and residential buildings (separate negotiation approach).
4. **Pricing model**: Set single or differential price per 5L unit. Offices pay premium, kitchens standard price. Subscription model for offices with guaranteed payment and volume cap. Water cost share of turnover: not determined (the brief's 30-50% was an example).
5. **IT & telemetry**: GPS tracker with SIM card, camera for remote monitoring, cashless API integration with a Serbian acquirer (card schemes to be confirmed with the acquirer; the earlier "Mirs" reference had no source and is removed), remote monitoring platform for water temperature (freeze protection). Monthly operating costs for data/software: not found.
6. **Operations**: Spare parts warehouse (filters, seals; cost not found), maintenance schedule and filter replacement interval (not found; ask the machine supplier).
7. **Scale**: Phase expansion starting with Serbia, then Balkan region. Franchise model for open zones where company itself is not present. Company handles equipment, warranty repair, training; franchisee handles local site acquisition.

## Nuances & Key Decisions
- **Cashless vs cash**: Cashless preferred in Serbia; cash treated cautiously. Complete cash rejection possible.
- **Single vs multiple machine configurations**: Office config (card payment) vs kitchen config (different features).
- **Pricing**: Test single price point first; differential pricing by location type later.
- **Tax splitting**: the brief mentions 20% for bottled water and 10% for other products (unconfirmed; the same numbers are the Serbian VAT rates). Need to calculate whether splitting flows is worth the administrative overhead.
- **Grants/subsidies**: Available to foreign-owned IP through Serbian government programs — startup grants, innovation subsidies, regional development support, Ministry of Foreign Affairs programs.
- **Franchise**: Only in permitted/open zones; company covers city itself. Franchisee pays a zone-dependent fee (amount not found, deferred). Company supplies equipment, handles warranty repair, provides training.
- **Heater risk**: Removable heater can be forgotten during cartridge replacement. Summer removal prevents theft but requires reinstallation logic.
- **Observability**: Remote understanding of machine state is critical — camera, telemetry, GPS must integrate easily without "a month-long integration on some bullshit protocol."
- **Repairability**: Spare parts warehouse must stock common parts; fast unit replacement without sending service cars for 3+ hours.

---

# Detailed End-to-End Implementation Plan

## Phase 1: Legal & Foundation
### 1.1 Register legal entity in Serbia (foreign-owned IP)
- Government (APR) fee for registering a new company from 1 Jan 2026: 8,000 RSD (about 68 EUR) **[verified]** https://biznis.rs/vesti/srbija/apr-ima-nove-cene-registracija-osnivanje-firme-8-000-dinara-promena-podataka-4-000-dinara/ ; entrepreneur (sole proprietor) 2,500 RSD. Lawyer/agent fees: not found, ask a Serbian lawyer. Since 15 May 2026 APR applications need an eID.gov.rs account (https://biznis.rs/vesti/srbija/apr-od-15-maja-sistem-prijavljivanja-na-portalu-sa-eservisima-iskljucivo-sa-korisnickim-nalogom/)
- Documentation: articles of incorporation, ID, address proof
- Outcome: Legal ability to operate business, open bank account, hire staff, sign contracts
- **Dependencies**: LEGAL:2.1

### 1.2 Determine tax regime assessment
- Brief: bottled water 20%, other products ("kisel" etc.) 10% (unconfirmed; equal to Serbian VAT rates 20% standard / 10% reduced, https://trykintsugi.com/sales-tax-guides/europe/serbia, secondary; the rate for vended water is not found)
- Calculate whether splitting flows (separate product categories) is worth the administrative overhead
- Consult a tax specialist (brief Sec 6.2)
- Outcome: Optimized tax structure for water vending business
- **Dependencies**: LEGAL:2.2

### 1.3 Research Serbian government grants/subsidies for foreign investors
- Programs: startup grants, innovation subsidies for green tech, regional development support, Ministry of Foreign Affairs support programs
- Eligibility criteria, application documents, expected amounts (RSD + EUR conversion)
- Document beneficiary type, program name, body, source URL
- Apply to all relevant programs simultaneously
- Outcome (2026-10-08): the earlier expectation of 50,000-200,000 EUR non-dilutive funding is NOT supported. Verified on opened pages: Smart Start up to 5.4 million RSD (call until 16 Nov 2026, ownership conditions not found); Kapital za razvoj is a subsidized bank loan (borrower pays 2%), not a grant; the self-employment subsidy and "Vrati se i stvaraj" are not available to a foreign founder. See `docs/cost-estimates/blocks/GRANTS_AND_SUPPORT.md` and fact 0005
- **Dependencies**: GRANTS_AND_SUPPORT:9.1-9.5

### 1.4 Prepare initial documentation package
- Business plan: concept, market analysis, financial projections, scale roadmap
- Financial plan: all cost estimates, pricing model, break-even analysis
- Cost estimates by blocks (TECH, FINANCE, MARKETING, LOCATIONS, IT_TELEMETRY, OPERATIONS, LEGAL, DOCUMENTATION)
- Project documentation: machine specs, placement strategy, operations plan
- Outcome: Complete package for banks, investors, grant applications, location negotiations
- **Dependencies**: DOCUMENTATION:8.1-8.4

## Phase 2: Technical Design & Machine Specification
### 2.1 Formalize machine technical requirements
- Principles: low cost, repairability, serviceability, observability, easy integration
- No "a month-long integration on some bullshit protocol"
- All tolerances and mismatches must be signed off with penalties
- Outcome: Technical specification document ready for procurement
- **Dependencies**: BRIEF:2.1; TECH:2.1

### 2.2 Select machine configuration and payment system
- **Priority**: cashless payment from phone (NFC → buy 5L water)
- Optional: coin acceptor, bill acceptor (cautious approach in Serbia)
- Consider complete cash rejection
- Office config: card payment emphasized
- Kitchen config: different feature set
- Outcome: Decided machine configuration(s) with bill of materials
- **Dependencies**: BRIEF:2.2; TECH:2.2; TECH:2.3

### 2.3 Select and procure machine modules
| Module | Description | Source/Assumption |
|--------|-------------|-------------------|
| 1.1 | Water vending machine - RO base unit (reader, GPS, camera, sensors and heater are separate lines 1.4-1.8) | Price not found; listings show US$500-1,050 (opened pages, not quotes) |
| 1.2 | Coin acceptor model selection | Not in pilot scope; price not found |
| 1.3 | Bill acceptor model selection | Not in pilot scope; price not found |
| 1.4 | Cashless payment module (phone NFC) | Reference: Nayax VPOS Touch US$390 (US store page opened); Serbian acquirer support to be confirmed |
| 1.5 | Camera module for monitoring (working/trashed/stolen scenarios) | Price not found; resolution and storage TBD |
| 1.6 | GPS tracker module | Price not found |
| 1.7 | Telemetry system (water temperature, freezing risk) | Price not found |
| 1.8 | Heater (removable/switchable, summer removal to prevent theft) | Price not found; risk: forgotten during cartridge replacement |
| 1.9 | Machine assembly coordination (contractor vs in-house) | Price not found; contractor quotes needed |
| 1.10 | Anti-vandalism protection (body and unit shielding) | Price not found; steel and polycarbonate construction |
- Outcome: All modules specified, priced when quotes arrive, and sourced ready for assembly
- **Dependencies**: TECH:1.1-1.10

### 2.4 Design anti-vandalism protection
- Steel housing + polycarbonate panels
- Protection for all units: coin acceptor, bill acceptor, cash module, water dispenser
- Tested resistance to common vandalism types (taping over, physical damage, theft attempts)
- Outcome: Protection design approved, cost estimated
- **Dependencies**: TECH:1.10; OPERATIONS:7.3

## Phase 3: Location Strategy & Site Acquisition
> **Pilot (2026-10-08):** start with one residential site near the founders' home (inside or at a building, separate electricity metering, rent not found; decision 0003). Office and kitchen work below is deferred until the pilot review.

### 3.1 Identify and negotiate target locations
**Offices**:
- Subscription model: guaranteed payment, volume cap ("we don't care how much you drink, but there must be a cap")
- Negotiate rent per site (price not found)
- Needed: electricity connection, accessible location, building management approval
- Outcome: Signed office lease agreements with subscription terms

**Professional areas (kitchens)**:
- Different machine configuration
- Negotiate terms separately
- Outcome: Signed kitchen location agreements

**Residential buildings**:
- Different approach than offices
- Lower density, different payment psychology
- Outcome: Selected residential pilot sites

- Outcome: 3-5 secured locations (mix of office + kitchen)
- **Dependencies**: BRIEF:3.1-3.3; LOCATIONS:5.1-5.5

### 3.2 Install electricity consumption tracking
- One-time cost: not found (ask the electricity distributor and an electrician)
- Critical: few sites will connect for free
- Outcome: Metering installed at all locations, consumption data available
- **Dependencies**: FINANCE:3.2; LOCATIONS:5.2

### 3.3 Set up subscription models for offices (deferred until pilot review)
- Volume cap negotiation per office
- Guaranteed payment structure
- Monthly rental (not found) + water cost per 5L unit
- Outcome: Office subscription contracts signed, first wave of office placements
- **Dependencies**: BRIEF:3.3; MARKETING:4.3

## Phase 4: Pricing, Marketing & IT Setup
### 4.1 Determine pricing model
- **Option A**: Single price per 5L unit (pilot: 50 RSD, owner decision 0004) — test first, optimize later
- **Option B**: Differential pricing by location type
  - Offices: premium price
  - Kitchens: standard price
- Outcome: Pricing strategy decided, incorporated into business plan
- **Dependencies**: MARKETING:4.1-4.2

### 4.2 Negotiate water supplier contracts
- 5L unit price negotiation
- Water cost share of turnover: not determined (the brief's 30-50% was an example)
- Supplier contracts signed, delivery schedule established
- Outcome: Reliable water supply at known cost
- **Dependencies**: FINANCE:3.1

### 4.3 Set up cashless payment integration
- Integrate with a Serbian acquirer (NFC phone payments; supported card schemes to be confirmed with the acquirer)
- API integration cost: not found (ask the acquirer / payment module supplier)
- Transaction fees: not found (FINANCE:3.5); ask the acquirer
- Test: phone button press → buy 5L water successfully
- Outcome: Working cashless payment flow from customer to machine
- **Dependencies**: IT_TELEMETRY:6.5; FINANCE:3.5

### 4.4 Deploy IT & telemetry infrastructure
| Component | Description | Frequency | Assumption |
|-----------|-------------|-----------|------------|
| GPS tracker hardware | Module with SIM card slot | One-time | price not found |
| GPS tracker subscription | Data plan for tracker | Monthly | price not found |
| Camera system | Remote monitoring (working/trashed/stolen) | One-time | price not found |
| Telemetry - water temp | Freeze protection monitoring | One-time | price not found |
| Payment integration | Cashless API with Serbian providers | One-time | price not found |
| Remote monitoring platform | Software subscription | Monthly | price not found |
- Outcome: All machines remotely monitorable, alerts sent for anomalies
- **Dependencies**: IT_TELEMETRY:6.1-6.6

### 4.5 Define marketing mix (4 Ps) and franchise parameters
- **Product**: Purified, drinkable water (filtered, not tap; not "globus" store water)
- **Price**: Determined pricing model per 5L unit
- **Place**: Selected locations (offices, kitchens, residential)
- **Promotion**: Local marketing, franchisee support, brand quality monitoring
- **Franchise zones**: Open zones where franchisee operates; company covers city itself
- Zone fee: not found (deferred until the pilot gate)
- Outcome: Complete marketing plan and franchise framework
- **Dependencies**: MARKETING:4.5; BRIEF:5.2

## Phase 5: Operations & First Deployment
### 5.1 Prepare spare parts warehouse
- Stock common parts: filters, seals, O-rings, small components
- Initial inventory: cost not found (spare parts list from the machine supplier)
- Goal: fast replacement without long downtimes
- Outcome: Warehouse stocked, ready for maintenance
- **Dependencies**: OPERATIONS:7.1

### 5.2 Define service intervals and maintenance scheduling
- Service interval: not found (a quarterly visit was a proposal; confirm with the supplier)
- Maintenance tasks: filter replacement, cleaning, calibration check, telemetry verification
- Service cost: TBD (spare parts + technician time)
- Outcome: Maintenance schedule established, service providers identified
- **Dependencies**: OPERATIONS:7.2; FINANCE:3.3

### 5.3 Install first machine at pilot location
- Machine assembly with all modules
- Connection: payment system, GPS tracker, camera, telemetry sensors
- Configuration: payment settings, subscription terms, pricing
- Testing: all functions (payment, dispensing, monitoring, alerts)
- Outcome: First machine operational at pilot site
- **Dependencies**: TECH:1.1-1.10; IT_TELEMETRY:6.1-6.6; LOCATIONS:5.1

### 5.4 Launch cashless payment and first sales
- Customer presses button on phone (NFC) → purchases 5L water
- Machine dispenses purified water
- Telemetry sends confirmation to remote platform
- First revenue generated
- Outcome: First successful water purchase completed ✅
- **Dependencies**: All prior phases completed

## Phase 6: Scale & Optimize
### 6.1 Monitor pilot performance
- Sales volume, payment success rate
- Maintenance needs and downtime
- Customer feedback
- Telemetry alerts and responses

### 6.2 Optimize pricing and operations
- Adjust price per 5L unit based on actual data
- Refine subscription terms per office feedback
- Optimize filter replacement schedule
- Reduce operational costs

### 6.3 Expand to additional locations
- **Gate (decision 0011):** only after the pilot averages ≥50 L/day at ≥95% uptime for 3 consecutive months
- Apply lessons learned from pilot
- Recruit new office clients
- Add kitchen and residential placements
- Target number of machines: not determined (depends on pilot results)

### 6.4 Consider franchise expansion
- **Gate (decision 0011):** same pilot gate as 6.3
- If pilot successful, evaluate franchise model
- Identify open zones in other Serbian cities or Balkan countries
- Sign franchise agreements with trained franchisees
- Company provides equipment, support, training

### 6.5 Scale business plan and financials
- Update business plan with actual data
- Revise financial projections
- Prepare for Series A or external investment if needed
- Outcome: Scalable business ready for regional expansion