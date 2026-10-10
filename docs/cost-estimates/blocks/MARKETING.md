# MARKETING Cost Estimate

| item | description | unit | quantity | unit price | total | frequency | assumption | source |
|------|-------------|------|----------|------------|-------|-----------|------------|--------|
| 4.1 | Single price model per 5L unit | 5L unit | 1 | 0.4257 | 0.4257 | per unit | Pilot price is 50 RSD per 5 L (owner decision, decision 0004); 50 / 117.4601 = 0.4257 EUR. Excluded from totals (revenue, not a cost) | [source: docs/decisions/0004-single-price-first.md (owner decision)] |
| 4.2 | Different price by location type (office vs kitchen) | 5L unit | 1 | not found | not found | per unit | NOT FOUND. Differential price by location type is deferred (decision 0004). Needed: pilot data and owner decision. | [source: none - not found, no opened source] |
| 4.3 | Subscription model for offices (volume cap) | monthly | 1 | not found | not found | monthly | NOT FOUND. Office subscription price is deferred (decision 0003). Needed: pilot data and owner decision. | [source: none - not found, no opened source] |
| 4.4 | Franchise scaling to Balkan region | zone | 1 | not found | not found | one-time | NOT FOUND. Franchise scaling cost is deferred (decisions 0006, 0011). Needed: owner decision after the pilot gate. | [source: none - not found, no opened source] |
| 4.5 | Marketing Ps (Product, Price, Place, Promotion) analysis | analysis | 1 | not found | not found | one-time | NOT FOUND. Price of a marketing mix analysis is unknown; could be done internally. Needed: consultancy quote or decision to do it internally. | [source: none - not found, no opened source] |

---

*Notes:*
- All prices in EUR unless otherwise noted. RSD amounts converted at 1 EUR = 117.4601 RSD, 1 USD = 104.7068 RSD (pipeline/fx.py, NBS data of 2026-10-06 via biznis.kurir.rs, secondary).
- A cell with 'not found' means no price was found on an opened source; the assumption cell says what is needed and whom to ask. Such rows are skipped in all totals and reported by pipeline/calculator.py. Register: docs/reports/unknowns-and-open-issues.md.
