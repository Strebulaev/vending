# OPERATIONS Cost Estimate

| item | description | unit | quantity | unit price | total | frequency | assumption | source |
|------|-------------|------|----------|------------|-------|-----------|------------|--------|
| 7.1 | Machine repairability - spare parts warehouse setup | warehouse | 1 | not found | not found | one-time | NOT FOUND. Initial spare parts stock cost is unknown. Needed: spare parts and consumables list with prices from the chosen machine supplier. | [source: none - not found, no opened source] |
| 7.2 | Service interval and maintenance scheduling | service | 1 | not found | not found | per service | NOT FOUND. Price of a service visit is unknown. Needed: service contract quote (ask the machine supplier or a local contractor). Partly overlaps FINANCE 3.3. | [source: none - not found, no opened source] |
| 7.3 | Anti-vandalism body protection | unit | 1 | not found | not found | one-time | NOT FOUND. Duplicate of TECH 1.10 (excluded). | [source: none - not found, no opened source] |

---

*Notes:*
- All prices in EUR unless otherwise noted. RSD amounts converted at 1 EUR = 117.4601 RSD, 1 USD = 104.7068 RSD (pipeline/fx.py, NBS data of 2026-10-06 via biznis.kurir.rs, secondary).
- A cell with 'not found' means no price was found on an opened source; the assumption cell says what is needed and whom to ask. Such rows are skipped in all totals and reported by pipeline/calculator.py. Register: docs/reports/unknowns-and-open-issues.md.
