"""Calculate CAPEX/OPEX totals and payback from all estimate blocks."""

import os
import re
from fx import to_rsd, to_eur

PIPELINE_DIR = "docs/pipeline/estimates"
BLOCKS = [
    "TECH", "LEGAL", "FINANCE", "MARKETING", "LOCATIONS",
    "IT_TELEMETRY", "OPERATIONS", "DOCUMENTATION",
    "GRANTS_AND_SUPPORT", "INTEGRATION",
]

# Currency per block (from source analysis)
BLOCK_CURRENCY = {
    "TECH": "EUR",
    "LEGAL": "EUR",
    "FINANCE": "EUR",
    "MARKETING": "EUR",
    "LOCATIONS": "EUR",
    "IT_TELEMETRY": "EUR",
    "OPERATIONS": "EUR",
    "DOCUMENTATION": "EUR",
    "GRANTS_AND_SUPPORT": "RSD",
    "INTEGRATION": "EUR",
}


def parse_block(block_name):
    path = os.path.join(PIPELINE_DIR, f"{block_name}.md")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    rows = []
    in_table = False
    for line in content.split("\n"):
        if line.startswith("| item") or line.startswith("|------"):
            in_table = True
            continue
        if in_table and line.startswith("|") and not line.startswith("|----"):
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if len(cells) >= 9:
                rows.append({
                    "item": cells[0],
                    "description": cells[1],
                    "unit": cells[2],
                    "quantity": cells[3],
                    "unit_price": cells[4],
                    "total": cells[5],
                    "frequency": cells[6],
                    "assumption": cells[7],
                    "source": cells[8],
                })
    return rows


def main():
    capex_by_block = {}
    opex_by_block = {}

    for block in BLOCKS:
        rows = parse_block(block)
        currency = BLOCK_CURRENCY.get(block, "EUR")
        capex = 0.0
        opex = 0.0
        for row in rows:
            total = row["total"]
            if not total or not total.strip():
                continue
            if total.endswith("%"):
                continue
            try:
                amount = float(total)
            except ValueError:
                continue
            amount_rsd = to_rsd(amount, currency)
            freq = row["frequency"].lower()
            if "one-time" in freq:
                capex += amount_rsd
            elif "monthly" in freq or "per unit" in freq or "per service" in freq or "per transaction" in freq:
                opex += amount_rsd
        capex_by_block[block] = capex
        opex_by_block[block] = opex

    total_capex = sum(capex_by_block.values())
    total_opex_monthly = sum(opex_by_block.values())
    total_opex_yearly = total_opex_monthly * 12

    # Residential pilot baseline (decision 0003, fact 0007): 50 RSD per 5 L.
    # OPEX comes from the estimates (cash costs, no amortization), so payback
    # = CAPEX / (revenue - OPEX - tax) does not double-count equipment cost.
    price_per_liter = 10  # RSD
    tax_rate = 0.10
    scenarios = {"консервативный": 50, "реалистичный": 80}  # liters per day

    results = {}
    for name, liters_per_day in scenarios.items():
        liters_per_month = liters_per_day * 30
        revenue = price_per_liter * liters_per_month
        tax = revenue * tax_rate
        net = revenue - total_opex_monthly - tax
        payback = total_capex / net if net > 0 else float("inf")
        results[name] = (liters_per_day, liters_per_month, revenue, tax, net, payback)

    lines = []
    lines.append("# Сценарии пилотной точки\n")
    lines.append("")
    lines.append("## 1. Затраты\n")
    lines.append(f"- **CAPEX всего:** {total_capex:,.0f} RSD (~{to_eur(total_capex, 'RSD'):,.0f} EUR)")
    lines.append(f"- **OPEX в месяц:** {total_opex_monthly:,.0f} RSD (~{to_eur(total_opex_monthly, 'RSD'):,.0f} EUR)")
    lines.append(f"- **OPEX в год:** {total_opex_yearly:,.0f} RSD (~{to_eur(total_opex_yearly, 'RSD'):,.0f} EUR)")
    lines.append("")
    lines.append("## 2. CAPEX по блокам\n")
    lines.append("| Блок | Сумма (RSD) | Сумма (EUR) |")
    lines.append("|------|-------------|-------------|")
    for block, amount in capex_by_block.items():
        lines.append(f"| {block} | {amount:,.0f} | {to_eur(amount, 'RSD'):,.0f} |")
    lines.append(f"| **ИТОГО** | **{total_capex:,.0f}** | **{to_eur(total_capex, 'RSD'):,.0f}** |")
    lines.append("")
    lines.append("## 3. OPEX по блокам (в месяц)\n")
    lines.append("| Блок | Сумма (RSD) | Сумма (EUR) |")
    lines.append("|------|-------------|-------------|")
    for block, amount in opex_by_block.items():
        lines.append(f"| {block} | {amount:,.0f} | {to_eur(amount, 'RSD'):,.0f} |")
    lines.append(f"| **ИТОГО** | **{total_opex_monthly:,.0f}** | **{to_eur(total_opex_monthly, 'RSD'):,.0f}** |")
    lines.append("")
    lines.append(f"## 4. Сценарии (цена {price_per_liter} RSD/л = {price_per_liter * 5} RSD за 5 л, налог {tax_rate:.0%})\n")
    lines.append("| Сценарий | л/день | Выручка/мес (RSD) | Налог (RSD) | Чистая прибыль/мес (RSD) | Окупаемость (мес) |")
    lines.append("|----------|--------|-------------------|-------------|--------------------------|-------------------|")
    for name, (lpd, lpm, revenue, tax, net, payback) in results.items():
        lines.append(f"| {name} | {lpd} | {revenue:,.0f} | {tax:,.0f} | {net:,.0f} | {payback:.1f} |")
    lines.append("")
    lines.append("## 5. Источники\n")
    lines.append("- Затраты: docs/pipeline/estimates/*.md")
    lines.append("- Курсы валют: fx.py (NBS reference)")
    lines.append("- Допущения: docs/decisions/0003-residential-single-point-pilot.md, docs/facts/0007-pilot-financials.md")
    lines.append("- Гранты в расчёт не включены: доступна иностранцам только программа-кредит (docs/facts/0005-grant-eligibility-foreigners.md)")

    out = "docs/pipeline/consolidated/pilot_scenarios.md"
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))
    print(f"Created {out}")
    for name, (lpd, lpm, revenue, tax, net, payback) in results.items():
        print(f"{name}: {lpd} L/day, revenue {revenue:,.0f}, net {net:,.0f}, payback {payback:.1f} mo")


if __name__ == "__main__":
    main()
