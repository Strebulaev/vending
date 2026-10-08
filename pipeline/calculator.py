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

# Pilot scope (decisions 0001, 0003, 0005, 0011): one residential machine, cashless only.
# Every estimate row must be classified here; unclassified rows abort the run so
# new rows cannot silently change the totals.
#   hardware - one-time machine and install cost
#   soft     - one-time professional services (unverified, reported separately)
#   fixed    - monthly cost; the number is months per period (3 = quarterly)
#   exclude  - not a pilot cost, with the reason
SCOPE = {
    "1.1": ("hardware",), "1.2": ("exclude", "приём наличных вне пилота (решение 0001)"),
    "1.3": ("exclude", "приём наличных вне пилота (решение 0001)"),
    "1.4": ("hardware",), "1.5": ("hardware",), "1.6": ("hardware",), "1.7": ("hardware",),
    "1.8": ("hardware",), "1.9": ("hardware",), "1.10": ("hardware",),
    "2.1": ("soft",), "2.2": ("soft",), "2.3": ("soft",),
    "2.4": ("exclude", "франшиза отложена (решения 0005, 0011)"),
    "3.1": ("exclude", "переменная стоимость воды считается по тарифу (факт 0003); строка противоречит ему"),
    "3.2": ("exclude", "дубль аренды 5.1"),
    "3.3": ("fixed", 1), "3.4": ("fixed", 3),
    "3.5": ("exclude", "комиссия считается от выручки"),
    "3.6": ("exclude", "франшиза отложена (решения 0005, 0011)"),
    "4.1": ("exclude", "цена пилота 50 RSD за 5 л (решение 0004); строка (2 EUR за 5 л) ей противоречит"),
    "4.2": ("exclude", "дифференцированная цена отложена (решение 0004)"),
    "4.3": ("exclude", "офисные подписки отложены (решение 0003)"),
    "4.4": ("exclude", "масштабирование на Балканы отложено (решения 0006, 0011)"),
    "4.5": ("soft",),
    "5.1": ("fixed", 1), "5.2": ("hardware",),
    "5.3": ("exclude", "офисы отложены (решение 0003)"),
    "5.4": ("exclude", "кухни отложены (решение 0003)"),
    "5.5": ("hardware",),
    "6.1": ("exclude", "дубль GPS 1.6"), "6.2": ("fixed", 1),
    "6.3": ("exclude", "дубль камеры 1.5"), "6.4": ("exclude", "дубль датчиков 1.7"),
    "6.5": ("hardware",), "6.6": ("fixed", 1),
    "7.1": ("hardware",), "7.2": ("fixed", 3),
    "7.3": ("exclude", "дубль антивандальной защиты 1.10"),
    "8.1": ("soft",), "8.2": ("soft",), "8.3": ("soft",), "8.4": ("soft",),
    **{f"9.{i}": ("exclude", "источник финансирования, а не расход") for i in range(1, 7)},
    **{f"10.{i}": ("hardware",) for i in range(1, 16)},
}

# Variable-cost assumptions
PRICE_PER_5L_RSD = 50          # decision 0004, presentation
WATER_TARIFF_RSD_M3 = 158.09   # fact 0003
REJECT_MULTIPLIER = 4          # ASSUMPTION: water drawn per litre sold incl. RO reject (confirm with supplier)
PAYMENT_FEE = 0.015            # lower bound of the 1.5-3% estimate (FINANCE 3.5)
TAX_RATE = 0.10                # flat tax on revenue (presentation)
SCENARIOS = {"консервативный": 50, "реалистичный": 80}  # liters per day

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
    hardware = {}
    soft = {}
    fixed_monthly_rsd = 0.0
    fixed_rows = []
    excluded = []
    for block in BLOCKS:
        currency = BLOCK_CURRENCY.get(block, "EUR")
        for row in parse_block(block):
            item = row["item"]
            if item not in SCOPE:
                raise SystemExit(f"Unclassified estimate row {item} in {block}: add it to SCOPE")
            kind, *rest = SCOPE[item]
            total = row["total"].strip() if row["total"] else ""
            if total.endswith("%") or not total:
                continue
            amount_rsd = to_rsd(float(total), currency)
            if kind == "exclude":
                excluded.append((item, block, row["description"], amount_rsd, rest[0]))
            elif kind == "hardware":
                hardware[block] = hardware.get(block, 0.0) + amount_rsd
            elif kind == "soft":
                soft[block] = soft.get(block, 0.0) + amount_rsd
            elif kind == "fixed":
                monthly = amount_rsd / rest[0]
                fixed_monthly_rsd += monthly
                fixed_rows.append((item, row["description"], monthly))

    capex_hw = sum(hardware.values())
    capex_soft = sum(soft.values())
    price_l = PRICE_PER_5L_RSD / 5
    water_l = WATER_TARIFF_RSD_M3 / 1000 * REJECT_MULTIPLIER
    contribution_l = price_l * (1 - PAYMENT_FEE - TAX_RATE) - water_l
    breakeven_lpd = fixed_monthly_rsd / contribution_l / 30

    results = {}
    for name, lpd in SCENARIOS.items():
        liters = lpd * 30
        revenue = price_l * liters
        variable = water_l * liters + revenue * PAYMENT_FEE
        tax = revenue * TAX_RATE
        net = revenue - variable - tax - fixed_monthly_rsd
        pay_hw = capex_hw / net if net > 0 else None
        pay_all = (capex_hw + capex_soft) / net if net > 0 else None
        results[name] = (lpd, revenue, variable, tax, net, pay_hw, pay_all)

    def eur(v):
        return f"{to_eur(v, 'RSD'):,.0f}"

    def months(v):
        return f"{v:.1f}" if v is not None else "не окупается"

    L = []
    L.append("# Сценарии пилотной точки\n")
    L.append("Расчёт `pipeline/calculator.py` для одного жилого аппарата, только безналичная оплата (решения 0001, 0003, 0005, 0011). Каждая строка смет классифицирована в `SCOPE`; исключения и причины — в разделе 6.\n")
    L.append("## 1. Единовременные затраты: оборудование и установка\n")
    L.append("| Блок | RSD | EUR |")
    L.append("|------|-----|-----|")
    for block, amount in hardware.items():
        L.append(f"| {block} | {amount:,.0f} | {eur(amount)} |")
    L.append(f"| **ИТОГО** | **{capex_hw:,.0f}** | **{eur(capex_hw)}** |")
    L.append("")
    L.append("## 2. Единовременные услуги (не проверены)\n")
    L.append("Строки смет без подтверждённых источников; заметная часть, вероятно, завышена (например, LEGAL 2.1 противоречит плану по валюте). Показаны отдельно и не входят в основной срок окупаемости.\n")
    L.append("| Блок | RSD | EUR |")
    L.append("|------|-----|-----|")
    for block, amount in soft.items():
        L.append(f"| {block} | {amount:,.0f} | {eur(amount)} |")
    L.append(f"| **ИТОГО** | **{capex_soft:,.0f}** | **{eur(capex_soft)}** |")
    L.append("")
    L.append("## 3. Постоянные расходы в месяц\n")
    L.append("| Строка | Описание | RSD/мес |")
    L.append("|--------|----------|---------|")
    for item, desc, monthly in fixed_rows:
        L.append(f"| {item} | {desc} | {monthly:,.0f} |")
    L.append(f"| | **ИТОГО** | **{fixed_monthly_rsd:,.0f}** (~{eur(fixed_monthly_rsd)} EUR) |")
    L.append("")
    L.append("## 4. Переменные расходы и допущения\n")
    L.append(f"- Цена: {PRICE_PER_5L_RSD} RSD за 5 л ({price_l:.0f} RSD/л).")
    L.append(f"- Вода: тариф {WATER_TARIFF_RSD_M3} RSD/м³, забор в {REJECT_MULTIPLIER} раза больше проданного объёма из-за сброса RO (допущение, уточнить у поставщика): {water_l:.2f} RSD/л.")
    L.append(f"- Комиссия платёжного провайдера: {PAYMENT_FEE:.1%} выручки (нижняя граница 1,5–3%).")
    L.append(f"- Налог: {TAX_RATE:.0%} выручки.")
    L.append(f"- Вклад с литра после переменных затрат: {contribution_l:.2f} RSD.")
    L.append("")
    L.append("## 5. Сценарии\n")
    L.append("| Сценарий | л/день | Выручка/мес | Переменные | Налог | Чистая прибыль/мес | Окупаемость оборудования (мес) | Окупаемость с услугами (мес) |")
    L.append("|----------|--------|-------------|-----------|-------|--------------------|-------------------------------|------------------------------|")
    for name, (lpd, revenue, variable, tax, net, pay_hw, pay_all) in results.items():
        L.append(f"| {name} | {lpd} | {revenue:,.0f} | {variable:,.0f} | {tax:,.0f} | {net:,.0f} | {months(pay_hw)} | {months(pay_all)} |")
    L.append("")
    L.append(f"**Безубыточность по текущим расходам: ≈{breakeven_lpd:.0f} л/день.**\n")
    L.append("## 6. Исключённые строки смет\n")
    L.append("| Строка | Блок | Описание | RSD | Причина |")
    L.append("|--------|------|----------|-----|---------|")
    for item, block, desc, amount, reason in excluded:
        L.append(f"| {item} | {block} | {desc} | {amount:,.0f} | {reason} |")
    L.append("")
    L.append("## 7. Источники\n")
    L.append("- Затраты: docs/pipeline/estimates/*.md; курсы: fx.py (NBS).")
    L.append("- Допущения: решения 0001, 0003, 0004, 0011; факты 0003, 0005, 0007.")

    out = "docs/pipeline/consolidated/pilot_scenarios.md"
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L))
    print(f"Created {out}")
    print(f"hardware CAPEX {capex_hw:,.0f} RSD; soft {capex_soft:,.0f} RSD; fixed OPEX {fixed_monthly_rsd:,.0f} RSD/mo; break-even {breakeven_lpd:.0f} L/day")
    for name, (lpd, revenue, variable, tax, net, pay_hw, pay_all) in results.items():
        print(f"{name}: {lpd} L/day, revenue {revenue:,.0f}, net {net:,.0f}, payback hw {months(pay_hw)}, with services {months(pay_all)}")


if __name__ == "__main__":
    main()
