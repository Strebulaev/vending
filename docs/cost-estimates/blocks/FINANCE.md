# FINANCE Cost Estimate

| item | description | unit | quantity | unit price | total | frequency | assumption | source |
|------|-------------|------|----------|------------|-------|-----------|------------|--------|
| 3.1 | Water cost per 5L unit (supplier contract) | 5L unit | 1 | not found | not found | per unit | NOT FOUND. Formula: cost per 5 L unit (RSD) = 5 x k x (158.09 + 85.07) / 1000, where k = litres of water drawn per litre sold (RO reject included) is unknown. Tariffs are for Belgrade BVK, other consumers, 2026, incl. VAT, secondary source; whether wastewater is charged on the drawn volume is unknown. Needed: reject ratio of the chosen machine (ask the supplier) and the wastewater billing rule (ask BVK). Excluded from the scenario totals (water is computed per litre separately) | [source: `material/economics/web-archive/beograduzivo.rs_8f518c21`] |
| 3.2 | Monthly site rent/electricity cost per site | site | 1 | not found | not found | monthly | NOT FOUND. Rent/electricity per site is unknown (the figure of 150 EUR in the project brief was an illustrative remark, not a quote). Needed: a written offer from the building owner or residents. Duplicate of LOCATIONS 5.1 (excluded here). | [source: none - not found, no opened source] |
| 3.3 | Maintenance and repair cost per site | site | 1 | not found | not found | monthly | NOT FOUND. Maintenance and repair cost per site per month is unknown. Needed: a service contract quote (ask the machine supplier or a local service contractor). Partly overlaps OPERATIONS 7.2. | [source: none - not found, no opened source] |
| 3.4 | Filter replacement cartridge | cartridge | 1 | not found | not found | every 3 months | NOT FOUND. Filter cartridge price and replacement interval are unknown. Needed: the consumables list of the chosen machine with prices (ask the supplier, see supplier-rfq.md). | [source: none - not found, no opened source] |
| 3.5 | Cashless payment transaction fee | transaction | 1 | not found | not found | per transaction | NOT FOUND. Cashless transaction fee (percent of revenue) is unknown; no Serbian acquirer tariff found. Needed: tariff of a Serbian acquirer or payment provider (ask banks / the payment module supplier). Applied as a percentage of revenue in pipeline/calculator.py once known | [source: none - not found, no opened source] |
| 3.6 | Franchise fee (if applicable) per zone | franchise zone | 1 | not found | not found | one-time | NOT FOUND. Franchise zone fee is unknown; franchise is excluded from the pilot (decisions 0005, 0011). Needed: owner decision after the pilot gate. | [source: none - not found, no opened source] |

---

*Notes:*
- All prices in EUR unless otherwise noted. RSD amounts converted at 1 EUR = 117.4601 RSD, 1 USD = 104.7068 RSD (pipeline/fx.py, NBS data of 2026-10-06 via biznis.kurir.rs, secondary).
- A cell with 'not found' means no price was found on an opened source; the assumption cell says what is needed and whom to ask. Such rows are skipped in all totals and reported by pipeline/calculator.py. Register: docs/reports/unknowns-and-open-issues.md.
