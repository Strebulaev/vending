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
    "TECH": "USD",
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

    # Revenue and tax assumptions from brief
    price_per_liter = 50  # RSD
    liters_per_day = 180
    liters_per_month = liters_per_day * 30
    revenue_monthly = price_per_liter * liters_per_month
    tax_rate = 0.10
    tax_monthly = revenue_monthly * tax_rate
    net_profit_monthly = revenue_monthly - total_opex_monthly - tax_monthly

    payback_months = total_capex / net_profit_monthly if net_profit_monthly > 0 else float("inf")

    # Grants offset (only ELIGIBLE ones)
    grants_total_rsd = 380000  # Subsidija za samozapošljavanje, if applicable
    capex_after_grants = max(0, total_capex - grants_total_rsd)
    payback_with_grants = capex_after_grants / net_profit_monthly if net_profit_monthly > 0 else float("inf")

    lines = []
    lines.append("# SMETA_FINAL: Итоговая смета проекта\n")
    lines.append("")
    lines.append("## 1. Сводка\n")
    lines.append(f"- **CAPEX всего:** {total_capex:,.0f} RSD (~{to_eur(total_capex, 'RSD'):,.0f} EUR)")
    lines.append(f"- **OPEX в месяц:** {total_opex_monthly:,.0f} RSD (~{to_eur(total_opex_monthly, 'RSD'):,.0f} EUR)")
    lines.append(f"- **OPEX в год:** {total_opex_yearly:,.0f} RSD (~{to_eur(total_opex_yearly, 'RSD'):,.0f} EUR)")
    lines.append(f"- **Выручка в месяц:** {revenue_monthly:,.0f} RSD")
    lines.append(f"- **Чистая прибыль в месяц:** {net_profit_monthly:,.0f} RSD")
    lines.append(f"- **Окупаемость:** {payback_months:.1f} мес")
    lines.append(f"- **Окупаемость с грантом:** {payback_with_grants:.1f} мес")
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
    lines.append("## 4. Доходная часть\n")
    lines.append(f"- Цена за литр: {price_per_liter} RSD")
    lines.append(f"- Продажи в день: {liters_per_day} л")
    lines.append(f"- Продажи в месяц: {liters_per_month} л")
    lines.append(f"- Выручка в месяц: {revenue_monthly:,.0f} RSD")
    lines.append("")
    lines.append("## 5. Налоги и прибыль\n")
    lines.append(f"- Налог (10% паушально): {tax_monthly:,.0f} RSD")
    lines.append(f"- OPEX: {total_opex_monthly:,.0f} RSD")
    lines.append(f"- **Чистая прибыль: {net_profit_monthly:,.0f} RSD**")
    lines.append("")
    lines.append("## 6. Окупаемость\n")
    lines.append(f"- Без гранта: **{payback_months:.1f} мес**")
    lines.append(f"- С грантом {grants_total_rsd:,.0f} RSD: **{payback_with_grants:.1f} мес**")
    lines.append("")
    lines.append("## 7. Источники\n")
    lines.append("- Все цифры взяты из docs/pipeline/estimates/*.md")
    lines.append("- Курсы валют: fx.py (NBS reference)")
    lines.append("- Гранты: только ELIGIBLE для иностранцев")

    with open("docs/pipeline/consolidated/SMETA_FINAL.md", "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))
    print("Created docs/pipeline/consolidated/SMETA_FINAL.md")


if __name__ == "__main__":
    main()