"""Sum the known estimate rows, report unknown ones, give formulas for profit/break-even.

Unknown inputs are None / 'not found'; nothing is guessed (owner rule)."""

import os

from fx import to_rsd, to_eur

PIPELINE_DIR = "docs/cost-estimates/blocks"
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
    "3.1": ("exclude", "переменная стоимость воды считается отдельно по тарифу (факт 0003); строка исключена, чтобы не считать дважды"),
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

# Known inputs and unknown inputs (None = not found; never replaced by a guess).
PRICE_PER_5L_RSD = 50          # owner decision (decision 0004)
WATER_TARIFF_RSD_M3 = 158.09   # fact 0003 (BVK, other consumers, 2026, incl. VAT; secondary source)
WASTEWATER_TARIFF_RSD_M3 = 85.07  # fact 0003 (same source); billing rule for RO reject not found
REJECT_MULTIPLIER = None       # litres drawn per litre sold: not found (ask the machine supplier)
PAYMENT_FEE = None             # acquirer fee, share of revenue: not found (ask acquirers)
TAX_RATE = None                # tax on revenue / VAT treatment: not found (ask an accountant)
SCENARIOS = {"низкий объём": 50, "более высокий объём": 80}  # litres per day: free decision variable, not a forecast

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


def num(cell):
    """Return a float for a numeric cell, None for 'not found' or any other text."""
    try:
        return float(str(cell).strip())
    except (TypeError, ValueError):
        return None


def check_row(block, row, kind, divisor):
    """Fail on arithmetic errors and on a frequency text that contradicts SCOPE (numeric rows only)."""
    qty, price, total = num(row["quantity"]), num(row["unit_price"]), num(row["total"])
    if qty is not None and price is not None and total is not None:
        if abs(qty * price - total) > 0.01:
            raise SystemExit(f"{block} {row['item']}: quantity x unit price != total")
    freq = row["frequency"].lower()
    if kind == "fixed":
        ok = (divisor == 1 and freq == "monthly") or (
            divisor == 3 and ("3 months" in freq or "per service" in freq))
        if not ok:
            raise SystemExit(f"{block} {row['item']}: frequency '{row['frequency']}' contradicts SCOPE divisor {divisor}")
    elif kind in ("hardware", "soft") and freq not in ("one-time", "ongoing"):
        raise SystemExit(f"{block} {row['item']}: one-time scope but frequency '{row['frequency']}'")


def collect():
    """Sum the rows with a known total; report the rows with an unknown price. Nothing is guessed."""
    cats = {"hardware": {}, "soft": {}}
    counts = {"hardware": [0, 0], "soft": [0, 0], "fixed": [0, 0]}   # [known, in scope]
    unknown = {"hardware": [], "soft": [], "fixed": []}               # (block, item, description)
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
            check_row(block, row, kind, rest[0] if kind == "fixed" else None)
            total = num(row["total"])
            if kind == "exclude":
                excluded.append((item, block, row["description"],
                                 None if total is None else to_rsd(total, currency), rest[0]))
                continue
            counts[kind][1] += 1
            if total is None:
                unknown[kind].append((block, item, row["description"]))
                continue
            counts[kind][0] += 1
            amount_rsd = to_rsd(total, currency)
            if kind in cats:
                cats[kind][block] = cats[kind].get(block, 0.0) + amount_rsd
            else:
                monthly = amount_rsd / rest[0]
                fixed_monthly_rsd += monthly
                fixed_rows.append((item, row["description"], monthly))
    return cats, counts, unknown, fixed_monthly_rsd, fixed_rows, excluded


def missing_inputs():
    m = []
    if REJECT_MULTIPLIER is None:
        m.append("k - литров воды из сети на литр проданной (сброс RO): не найдено, спросить поставщика аппарата")
    if PAYMENT_FEE is None:
        m.append("f - комиссия эквайрера, доля выручки: не найдено, спросить банки-эквайреры")
    if TAX_RATE is None:
        m.append("t - налог на выручку / режим НДС для воды из аппарата: не найдено, спросить бухгалтера и Налоговую администрацию")
    return m


def main():
    cats, counts, unknown, fixed_known, fixed_rows, excluded = collect()
    capex_hw = sum(cats["hardware"].values())
    capex_soft = sum(cats["soft"].values())
    price_l = PRICE_PER_5L_RSD / 5
    miss = missing_inputs()

    def eur(v):
        return f"{to_eur(v, 'RSD'):,.0f}"

    def listing(kind):
        if not unknown[kind]:
            return ["Нет."]
        by = {}
        for block, item, desc in unknown[kind]:
            by.setdefault(block, []).append(f"{item} {desc}")
        return [f"- {b}: " + "; ".join(v) for b, v in by.items()]

    L = []
    L.append("# Сценарии пилотной точки\n")
    L.append("Сгенерировано `pipeline/calculator.py` для одного жилого аппарата, только безналичная оплата (решения 0001, 0003, 0005, 0011). Скрипт не подставляет догадки: ячейки сметы со значением `not found` пропускаются и перечисляются ниже; суммы показаны только как «по найденным позициям». Курсы: 1 EUR = 117,4601 RSD, 1 USD = 104,7068 RSD (`pipeline/fx.py`, НБС на 6.10.2026 через biznis.kurir.rs, вторичный источник); RSD округлены до динара, EUR до евро. Реестр неизвестного: `docs/reports/unknowns-and-open-issues.md`.\n")
    L.append("## 1. Единовременные затраты на оборудование и установку\n")
    k, n = counts["hardware"]
    L.append(f"**По найденным позициям: {k} из {n} позиций.** Итог по всем позициям не определён.\n")
    L.append("| Блок | RSD (найденные позиции) | EUR |")
    L.append("|------|-----|-----|")
    for block, amount in cats["hardware"].items():
        L.append(f"| {block} | {amount:,.0f} | {eur(amount)} |")
    L.append(f"| **По найденным позициям** | **{capex_hw:,.0f}** | **{eur(capex_hw)}** |")
    L.append("\nПозиции без найденной цены (в сумму не входят):\n")
    L += listing("hardware")
    L.append("")
    L.append("## 2. Единовременные услуги\n")
    k, n = counts["soft"]
    L.append(f"**По найденным позициям: {k} из {n} позиций.**\n")
    L.append("| Блок | RSD (найденные позиции) | EUR |")
    L.append("|------|-----|-----|")
    for block, amount in cats["soft"].items():
        L.append(f"| {block} | {amount:,.0f} | {eur(amount)} |")
    L.append(f"| **По найденным позициям** | **{capex_soft:,.0f}** | **{eur(capex_soft)}** |")
    L.append("\nПозиции без найденной цены (в сумму не входят):\n")
    L += listing("soft")
    L.append("")
    L.append("## 3. Постоянные расходы в месяц\n")
    k, n = counts["fixed"]
    L.append(f"**По найденным позициям: {k} из {n} позиций.** Сумма постоянных расходов F не определена.\n")
    if fixed_rows:
        L.append("| Строка | Описание | RSD/мес |")
        L.append("|--------|----------|---------|")
        for item, desc, monthly in fixed_rows:
            L.append(f"| {item} | {desc} | {monthly:,.0f} |")
        L.append(f"| | **По найденным позициям** | **{fixed_known:,.0f}** |")
    else:
        L.append("Ни одна постоянная статья не имеет найденной цены (сумма по найденным позициям: 0 из {n}).".format(n=n))
    L.append("\nПозиции без найденной цены (аренда, обслуживание, платформа мониторинга, SIM, фильтры):\n")
    L += listing("fixed")
    L.append("")
    L.append("## 4. Известные входные данные и формулы\n")
    L.append(f"- Цена (решение владельца, 0004): {PRICE_PER_5L_RSD} RSD за 5 л, то есть p = {price_l:.0f} RSD/л (включает ли цена НДС — не определено).")
    L.append(f"- Тариф BVK 2026, прочие потребители, с НДС (факт 0003, вторичный источник): вода {WATER_TARIFF_RSD_M3} RSD/м³, водоотведение {WASTEWATER_TARIFF_RSD_M3} RSD/м³; порядок начисления на сброс RO не найден.")
    L.append(f"- Вода на 1 л проданной воды: w = k × {WATER_TARIFF_RSD_M3}/1000 RSD (только вода) или k × ({WATER_TARIFF_RSD_M3} + {WASTEWATER_TARIFF_RSD_M3})/1000 RSD (с водоотведением), где k — не найдено.")
    L.append("- Вклад с литра: c = p × (1 − f − t) − w. Выручка в месяц при V л/день: R = p × V × 30 (по цене покупателя).")
    L.append("- Прибыль в месяц: P(V) = c × V × 30 − F. Безубыточность: V* = F / (30 × c).")
    L.append("\nНе найдены входные данные, без которых c, F, P и V* не определены:\n")
    for m in miss:
        L.append(f"- {m}")
    L.append("- F - постоянные расходы: найдена часть позиций, см. раздел 3 (аренда, обслуживание, платформа, SIM, фильтры: не найдено).")
    L.append("")
    L.append("## 5. Сценарии объёма\n")
    L.append("Объём в литрах в день — свободная переменная решения, не прогноз. Вычислима только выручка по цене покупателя; прибыль, налоги и окупаемость **не определены** (нужны k, f, t, F).\n")
    L.append("| Сценарий | л/день | Выручка/мес по цене покупателя, RSD | Чистая прибыль/мес | Окупаемость |")
    L.append("|----------|--------|-----------------------------------|--------------------|-------------|")
    for name, lpd in SCENARIOS.items():
        L.append(f"| {name} | {lpd} | {price_l * lpd * 30:,.0f} | не определено | не определено |")
    L.append("")
    L.append("Безубыточность: **не определена** (формула V* в разделе 4). Критерий пилота 50 л/день — минимум спроса, а не безубыточность (решение 0011).\n")
    L.append("## 6. Исключённые строки смет\n")
    L.append("| Строка | Блок | Описание | RSD | Причина |")
    L.append("|--------|------|----------|-----|---------|")
    for item, block, desc, amount, reason in excluded:
        a = "не найдено" if amount is None else f"{amount:,.0f}"
        L.append(f"| {item} | {block} | {desc} | {a} | {reason} |")
    L.append("")
    L.append("## 7. Источники\n")
    L.append("- Затраты: `docs/cost-estimates/blocks/*.md` (только строки с URL/путём как источником); курсы: `pipeline/fx.py`.")
    L.append("- Входные данные: решение 0004 (цена, решение владельца); факт 0003 (тарифы BVK, вторичный источник).")
    L.append("- Строки блока GRANTS_AND_SUPPORT выражены в RSD (BLOCK_CURRENCY); остальные блоки — в EUR.")

    out = "docs/cost-estimates/pilot-scenarios.md"
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L) + "\n")
    print(f"Created {out}")
    for kind in ("hardware", "soft", "fixed"):
        print(f"{kind}: known {counts[kind][0]} of {counts[kind][1]}; unknown rows: " +
              ", ".join(f"{b}:{i}" for b, i, _ in unknown[kind]))
    print(f"known sums: hardware {capex_hw:,.0f} RSD, soft {capex_soft:,.0f} RSD, fixed {fixed_known:,.0f} RSD/mo")
    print("Missing inputs for profit/break-even:")
    for m in miss:
        print("  -", m)


if __name__ == "__main__":
    main()
