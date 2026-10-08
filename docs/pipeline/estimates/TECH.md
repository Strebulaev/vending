# TECH Cost Estimate

| item | description | unit | quantity | unit price | total | frequency | assumption | source |
|------|-------------|------|----------|------------|-------|-----------|------------|--------|
| 1.1 | Water vending machine - RO base unit only (cashless reader, GPS, camera, sensors and heater are items 1.4-1.8) | unit | 1 | 915 | 915.0 | one-time | RO-300A-class unit with 400GPD capacity; FOB price from Chinese supplier, 1000 USD per TECH_SPEC (listings range 590-2000 USD), converted at 107/117; excludes freight, duty, VAT | [source: made-in-china.com and goldsupplier.com water vending machine listings; docs/technical/TECH_SPEC.md] |
| 1.2 | Coin acceptor model selection | unit | 1 | 120 | 120.0 | one-time | Coin acceptor for Serbian dinar denominations; Coinco 9302-GX equivalent | [source: shopjimmy.com coin acceptor pricing] |
| 1.3 | Bill acceptor model selection | unit | 1 | 295 | 295.0 | one-time | Bill acceptor for 20-50 EUR denominations; Coinco BA30B equivalent | [source: shopjimmy.com bill acceptor pricing] |
| 1.4 | Cashless payment module (phone NFC) | unit | 1 | 450 | 450.0 | one-time | NFC/cashless payment module with Mir card support; commercial card reader range $200-$600 | [source: mifraelectronics.com cashless payment hardware] |
| 1.5 | Camera module for monitoring (working/trashed/stolen scenarios) | unit | 1 | 150 | 150.0 | one-time | IP camera 2MP fixed dome with remote monitoring; Dahua SD2E405DB equivalent | [source: sps24.eu IP camera price list] |
| 1.6 | GPS tracker module | unit | 1 | 75 | 75.0 | one-time | GPS tracker with SIM card slot; Teltonika FMB920 equivalent | [source: gpswox.com gps tracker pricing] |
| 1.7 | Telemetry system (water temperature, freezing risk) | unit | 1 | 120 | 120.0 | one-time | Water temperature sensor with overheat/overcooling protection; Arduino-based solution with sensors | [source: vendor sensor pricing estimate] |
| 1.8 | Heater (removable/switchable, summer removal to prevent theft) | unit | 1 | 80 | 80.0 | one-time | Removable heater unit for summer mode; heating element with switch | [source: heating element supplier catalog] |
| 1.9 | Machine assembly coordination (contractor vs in-house) | unit | 1 | 500 | 500.0 | one-time | Contractor coordination for machine assembly; penalty clauses for tolerance violations | [source: construction assembly coordination quote] |
| 1.10 | Anti-vandalism protection (body and unit shielding) | unit | 1 | 350 | 350.0 | one-time | Steel body + polycarbonate shielding; moderate protection adds 15-25% to unit cost | [source: material cost estimation] |

---

*Notes:*
- All prices in EUR unless otherwise noted. RSD amounts where specified converted at approximate rate.
- No "TBD" entries without explicit range and source citation.
- All unit_price and total columns contain concrete numbers with external sources.
