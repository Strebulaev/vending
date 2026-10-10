# IT_TELEMETRY Cost Estimate

| item | description | unit | quantity | unit price | total | frequency | assumption | source |
|------|-------------|------|----------|------------|-------|-----------|------------|--------|
| 6.1 | GPS tracker hardware module | unit | 1 | not found | not found | one-time | NOT FOUND. Duplicate of TECH 1.6 (excluded). See 1.6. | [source: none - not found, no opened source] |
| 6.2 | GPS tracker subscription (data plan) | monthly | 1 | not found | not found | monthly | NOT FOUND. Monthly data plan of the tracker is unknown. Needed: tariff of a Serbian mobile operator or IoT SIM provider (ask operators). | [source: none - not found, no opened source] |
| 6.3 | Camera system for remote monitoring | unit | 1 | not found | not found | one-time | NOT FOUND. Duplicate of TECH 1.5 (excluded). See 1.5. | [source: none - not found, no opened source] |
| 6.4 | Telemetry - water temperature sensor | sensor | 1 | not found | not found | one-time | NOT FOUND. Duplicate of TECH 1.7 (excluded). See 1.7. | [source: none - not found, no opened source] |
| 6.5 | Payment integration (cashless API with Serbian providers) | integration | 1 | not found | not found | one-time | NOT FOUND. Cost of integrating the cashless API with a Serbian acquirer is unknown. Needed: acquirer / payment module supplier quote. Fiscalization (ESIR) requirement for vending machines per a 2023 source; current status not found | [source: none for price - not found; fiscal context https://www.fiscal-requirements.com/news/2332-is-it-required-for-serbian-vending-machines-to-be-certified] |
| 6.6 | Remote monitoring platform subscription | monthly | 1 | not found | not found | monthly | NOT FOUND. Monthly price of a remote monitoring platform is unknown. Needed: platform vendor price lists or a decision to self-host (then hosting price). | [source: none - not found, no opened source] |

---

*Notes:*
- All prices in EUR unless otherwise noted. RSD amounts converted at 1 EUR = 117.4601 RSD, 1 USD = 104.7068 RSD (pipeline/fx.py, NBS data of 2026-10-06 via biznis.kurir.rs, secondary).
- A cell with 'not found' means no price was found on an opened source; the assumption cell says what is needed and whom to ask. Such rows are skipped in all totals and reported by pipeline/calculator.py. Register: docs/reports/unknowns-and-open-issues.md.
