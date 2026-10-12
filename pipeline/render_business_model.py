#!/usr/bin/env python3
"""Generate a condition-based pilot business model from planning assumptions."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "config/business-model.json"
DEFAULT_REPORT = ROOT / "docs/project/business-model.md"
DEFAULT_PRESENTATION = ROOT / "docs/project/investor-presentation.md"


def number(value: float) -> str:
    rounded = math.floor(abs(value) + 0.5) * (-1 if value < 0 else 1)
    return f"{rounded:,}".replace(",", " ")


def up(value: float, places: int = 0) -> float | int:
    factor = 10**places
    result = math.ceil(value * factor - 1e-9) / factor
    return int(result) if places == 0 else result


def down(value: float, places: int = 0) -> float | int:
    factor = 10**places
    result = math.floor(value * factor + 1e-9) / factor
    return int(result) if places == 0 else result


def operating(demand: float, price: float, variable: float, uptime: float,
              opex: float, days: int) -> float:
    return demand * uptime * days * (price - variable) - opex


def cash_after_tax(result: float, rate: float) -> float:
    return result * (1 - rate) if result > 0 else result


def payback(capex: float, result: float, rate: float) -> float:
    cash = cash_after_tax(result, rate)
    return capex / cash if cash > 0 else math.inf


def render(data: dict) -> str:
    e = data["presentation_estimate"]
    base = e["scenarios"]["realistic"]
    days = e["days_month"]
    demand = e["launch_reference_demand_lpd"]
    price = base["price_rsd_l"]
    variable = base["variable_rsd_l"]
    uptime = base["uptime"]
    opex = base["fixed_rsd_month"]
    capex = base["capex_rsd"]
    tax = e["illustrative_cit_rate"]
    vat = e["vat_registered_overlay_rate"]
    depreciation = e["depreciable_equipment_rsd"] / e["depreciation_months"]
    green_months = e["investment_horizon_months"]
    red_months = e["depreciation_months"]

    if not (0 < uptime <= 1 and 0 <= tax < 1 and 0 <= vat < 1 and price > variable):
        raise ValueError("Некорректная цена, переменные расходы, доступность или налоговая ставка")
    if green_months <= 0 or red_months <= green_months:
        raise ValueError("Горизонт инвестиционного решения должен быть короче срока аппарата")
    if sum(e["monthly_fixed_breakdown_base"].values()) != opex:
        raise ValueError("Сумма статей OPEX не совпадает с базовым OPEX")
    if sum(e["capex_breakdown_base"].values()) != capex:
        raise ValueError("Сумма статей CAPEX не совпадает с базовым CAPEX")

    unit = price - variable
    monthly_litres = demand * uptime * days
    result = operating(demand, price, variable, uptime, opex, days)
    after_tax = cash_after_tax(result, tax)
    capex_return = payback(capex, result, tax)
    required_green = capex / (green_months * (1 - tax))
    required_yellow = capex / (red_months * (1 - tax))
    # Both payback thresholds exceed the assumed depreciation in this configuration.
    if required_yellow <= depreciation:
        raise ValueError("Для этих входов границы окупаемости и бухгалтерской прибыли расходятся")

    per_lpd = days * uptime * unit
    volume_green = up((opex + required_green) / per_lpd)
    volume_yellow = up((opex + required_yellow) / per_lpd)
    opex_green = down(monthly_litres * unit - required_green)
    opex_yellow = down(monthly_litres * unit - required_yellow)
    capex_green = down(after_tax * green_months)
    capex_yellow = down(after_tax * red_months)
    price_green = up(variable + (opex + required_green) / monthly_litres, 2)
    price_yellow = up(variable + (opex + required_yellow) / monthly_litres, 2)
    uptime_green = up((opex + required_green) / (demand * days * unit), 3)
    uptime_yellow = up((opex + required_yellow) / (demand * days * unit), 3)
    variable_green = down(price - (opex + required_green) / monthly_litres, 2)
    variable_yellow = down(price - (opex + required_yellow) / monthly_litres, 2)

    vat_price = price / (1 + vat)
    vat_result = operating(demand, vat_price, variable, uptime, opex, days)
    vat_payback = payback(capex, vat_result, tax)
    vat_credit_green = up(required_green - vat_result)
    vat_credit_yellow = up(required_yellow - vat_result)
    theoretical_recurring_vat = (opex + monthly_litres * variable) * vat / (1 + vat)

    current_demand = base["demand_lpd"]
    current_result = operating(current_demand, price, variable, uptime, opex, days)
    failure_opex = e["monthly_fixed_rsd"]["high"]
    failure_result = operating(demand, price, variable, uptime, failure_opex, days)
    harsh = e["scenarios"]["pessimistic"]
    harsh_result = operating(demand, harsh["price_rsd_l"], harsh["variable_rsd_l"],
                             harsh["uptime"], harsh["fixed_rsd_month"], days)

    accounting = e["monthly_fixed_breakdown_base"]["accounting"]
    local_opex = opex - accounting
    scale_rows = []
    for count in (1, 2, 5, 10):
        total_opex = count * local_opex + accounting
        per_machine = total_opex / count
        min_volume = up((per_machine + required_green) / per_lpd)
        scale_rows.append((count, total_opex, per_machine, min_volume))
    second_volume = scale_rows[1][3]
    ten_volume = scale_rows[3][3]
    ten_revenue = 10 * ten_volume * uptime * days * price * 12
    ten_opex = scale_rows[3][2]
    ten_vat_green = up((ten_opex + required_green) / (days * uptime * (vat_price - variable)))

    lines = [
        "# Когда работает пилотный водомат в Сурчине",
        "",
        f"**Ответ за 30 секунд.** При цене {number(price)} RSD/л, переменных расходах {variable:g} RSD/л, доступности {uptime:.0%}, OPEX {number(opex)} RSD/мес. и CAPEX {number(capex)} RSD точка возвращает CAPEX за {green_months} месяцев при **{number(volume_green)} л/день и выше**. Для решения о запуске используем совместный запас: **{number(demand)} л/день, цена ≥{number(price)}, OPEX ≤{number(opex)}, CAPEX ≤{number(capex)}, доступность ≥{uptime:.0%}, переменные ≤{variable:g}**; если компания не платит НДС, результат — **{number(result)} RSD/мес. до условного CIT**, **{number(after_tax)} после него**, возврат CAPEX — **{capex_return:.1f} мес.** Оценка спроса сейчас {number(current_demand)} л/день: результат **{number(current_result)} RSD/мес.**, запуск при таком спросе экономически не проходит.",
        "",
        f"**Как читаются зоны.** 🟢 Положительный результат после условной амортизации и возврат CAPEX за ≤{green_months} мес.; 🟡 положительный результат и возврат за {green_months}–{red_months} мес.; 🔴 убыток либо возврат дольше {red_months} мес. Условные {red_months} мес. взяты из срока амортизации аппарата, а целевые {green_months} мес. — критерий инвестиционного решения, не доказанный срок службы. CIT для сравнения = {tax:.0%} положительного денежного результата; фактический налог считается по налоговой базе компании.",
        "",
        f"Исходные диапазоны для оценки: CAPEX {number(e['capex_rsd']['low'])}–{number(e['capex_rsd']['high'])} RSD, OPEX {number(e['monthly_fixed_rsd']['low'])}–{number(e['monthly_fixed_rsd']['high'])} RSD/мес., цена {e['price_test_range_rsd_l']['low']:g}–{e['price_test_range_rsd_l']['high']:g} RSD/л. Это допущения без вероятностей сценариев.",
        "",
        "## Сводная таблица условий",
        "",
        f"Границы в строках ниже меняют **один параметр** при {number(demand)} л/день и остальных условиях из первого абзаца. Они не складываются друг с другом. Денежные пороги округлены до 1 RSD, цена — до 0,01 RSD/л, доступность — до 0,1 процентного пункта.",
        "",
        "| Параметр | 🟢 Работает | 🟡 На грани | 🔴 Не работает | Почему граница и что решаем |",
        "|---|---:|---:|---:|---|",
        f"| Спрос, л/день | ≥{number(volume_green)} | {number(volume_yellow)}–{number(volume_green-1)} | ≤{number(volume_yellow-1)} | Прибавка 1 л/день даёт {per_lpd:.2f} RSD/мес.; текущие {number(current_demand)} л/день — 🔴. |",
        f"| OPEX, RSD/мес. | ≤{number(opex_green)} | {number(opex_green+1)}–{number(opex_yellow)} | ≥{number(opex_yellow+1)} | При {number(demand)} л/день вклад {number(monthly_litres*unit)} RSD; после OPEX нужно оставить ≥{number(required_green)} RSD/мес. |",
        f"| CAPEX, RSD | ≤{number(capex_green)} | {number(capex_green+1)}–{number(capex_yellow)} | ≥{number(capex_yellow+1)} | При {number(demand)} л/день после условного CIT остаётся {number(after_tax)} RSD/мес.; цена аппарата определяет срок возврата. |",
        f"| Цена, RSD/л | ≥{price_green:.2f} | {price_yellow:.2f}–{price_green-0.01:.2f} | <{price_yellow:.2f} | Продаётся {number(monthly_litres)} л/мес.; каждый 1 RSD/л меняет результат на {number(monthly_litres)} RSD/мес. |",
        f"| Доступность | ≥{uptime_green*100:.1f}% | {uptime_yellow*100:.1f}–{(uptime_green-0.001)*100:.1f}% | <{uptime_yellow*100:.1f}% | 100% дают {number(demand*days*unit)} RSD вклада до OPEX; для запуска принят более строгий ориентир {uptime:.0%}. |",
        f"| Переменные, RSD/л | ≤{variable_green:.2f} | {variable_green+0.01:.2f}–{variable_yellow:.2f} | >{variable_yellow:.2f} | Каждый 1 RSD/л затрат уменьшает результат на {number(monthly_litres)} RSD/мес.; текущие {variable:g} — допущение. |",
        f"| НДС при цене {number(price)} RSD/л с налогом | Без регистрации: 🟢; плательщик: нужен эквивалент вычета ≥{number(vat_credit_green)} RSD/мес. | Плательщик с вычетом {number(vat_credit_yellow)}–{number(vat_credit_green-1)} RSD/мес. | Плательщик без вычета или <{number(vat_credit_yellow)} RSD/мес. | Без вычета результат {number(vat_result)} RSD/мес., возврат {vat_payback:.1f} мес.; вычет и возможное снижение CAPEX зависят от счетов. |",
        "",
        "**Решение по зонам:** зелёный результат допускает оценку запуска только для совместного пакета ниже; жёлтый не достигает целевых 36 месяцев; красный исключает закупку для данной комбинации условий. После изменения нескольких входов границы пересчитываются вместе.",
        "",
        f"**Ограничение по НДС.** Даже если все текущие переменные и регулярные расходы {number(opex + monthly_litres*variable)} RSD/мес. включают НДС {vat:.0%} и весь он допустим к вычету, арифметический максимум регулярного вычета — **{number(theoretical_recurring_vat)} RSD/мес.**, меньше зелёного порога {number(vat_credit_green)}. Поэтому плательщику НДС при этих расходах для возврата за {green_months} месяцев также нужны снижение эффективного CAPEX за счёт подтверждённого вычета по оборудованию, более высокая цена, больше продаж или ниже расходы. Реальная доля вычета — нет данных.",
        "",
        f"Расчёт порогов: результат `R = л/день × {days} × доступность × (цена − переменные) − OPEX`; денежный поток после условного CIT = `R × {1-tax:.2f}` при `R > 0`; возврат = `CAPEX / поток`. Для {green_months} месяцев нужен `R ≥ {number(required_green)} RSD/мес.`, для {red_months} месяцев — `R ≥ {number(required_yellow)} RSD/мес.`. Положительный результат после условной амортизации требует `R > {number(depreciation)}`. База: {number(e['depreciable_equipment_rsd'])} / {red_months} = {number(depreciation)} RSD/мес. Входные суммы CAPEX, OPEX, цены, спроса и переменных — допущения.",
        "",
        "## Минимальные условия запуска",
        "",
        f"Условия ниже образуют **один совместный пакет**, поэтому выполнение всех неравенств сохраняет результат не хуже {number(result)} RSD/мес. до условного CIT:",
        "",
        f"1. Спрос на выбранной точке **≥{number(demand)} л/день**; при текущей гипотезе {number(current_demand)} запуск экономически не проходит.",
        f"2. OPEX **≤{number(opex)} RSD/мес.**, переменные **≤{variable:g} RSD/л**.",
        f"3. CAPEX **≤{number(capex)} RSD**, цена покупателя **≥{number(price)} RSD/л**.",
        f"4. Фактическая доступность **≥{uptime:.0%}**.",
        f"5. Базовый вариант — компания не зарегистрирована плательщиком НДС. Если НДС применяется к цене покупателя, условия нужно пересчитать по подтверждённым вычетам и снижению CAPEX; просто сохранить цену {number(price)} RSD/л недостаточно.",
        "",
        f"При пакете {number(demand)} л/день: выручка {number(monthly_litres*price)} RSD/мес.; переменные расходы {number(monthly_litres*variable)}; результат {number(result)}; условный поток после CIT {number(after_tax)}; результат после амортизации {number(result-depreciation)}. Доходность и срок возврата не подтверждены продажами или котировками.",
        "",
        "## Точка отказа",
        "",
        f"- При {number(demand)} л/день, цене {number(price)} RSD/л и доступности {uptime:.0%} OPEX {number(failure_opex)} RSD/мес. даёт **{number(failure_result)} RSD/мес.**: убыток даже при таком объёме.",
        f"- Если одновременно цена {harsh['price_rsd_l']:g} RSD/л, переменные {harsh['variable_rsd_l']:g} RSD/л, доступность {harsh['uptime']:.0%} и OPEX {number(harsh['fixed_rsd_month'])}, результат при {number(demand)} л/день — **{number(harsh_result)} RSD/мес.**; CAPEX {number(harsh['capex_rsd'])} не возвращается.",
        f"- При НДС {vat:.0%} внутри цены {number(price)} RSD/л и нулевом подтверждённом вычете результат {number(vat_result)} RSD/мес., возврат CAPEX **{vat_payback:.1f} мес.**: дольше условной жизни аппарата. Это расчёт для плательщика НДС при неизменных валовых затратах; реальный вычет может изменить вывод.",
        "",
        "## Порог масштабирования",
        "",
        f"Вторая точка экономически имеет смысл, если первая **фактически** держит ≥{number(demand)} л/день и ≥{uptime:.0%} три месяца, а вторая способна продавать ≥{number(second_volume)} л/день при цене {number(price)} RSD/л, переменных {variable:g} RSD/л, CAPEX ≤{number(capex)} RSD и приведённом ниже OPEX. Спрос второй точки не должен отнимать продажи первой. Доходность первой сама по себе не доказывает спрос на другом адресе.",
        "",
        f"Расчёт общего OPEX — **допущение**, а не сетевой бюджет: {number(local_opex)} RSD/мес. локальных расходов на аппарат + одна бухгалтерия {number(accounting)} RSD/мес. на всю сеть. Других общих затрат, дополнительных сотрудников, логистики и скидок на CAPEX здесь нет.",
        "",
        "| Аппаратов | OPEX сети, RSD/мес. | OPEX на аппарат, RSD/мес. | Минимум л/день на аппарат для возврата CAPEX за 36 мес. без НДС |",
        "|---:|---:|---:|---:|",
    ]
    for count, total_opex, per_machine, min_volume in scale_rows:
        lines.append(f"| {count} | {number(total_opex)} | {number(per_machine)} | {number(min_volume)} |")
    lines.extend([
        "",
        f"При 10 аппаратах даже минимальные {number(ten_volume)} л/день на каждый дают около **{number(ten_revenue)} RSD** розничного оборота за 12 условных месяцев — выше порога регистрации НДС 8 млн RSD по общему обороту компании за предыдущие 12 месяцев. Значит, строку на 10 аппаратов нельзя использовать как решение без пересчёта НДС. При НДС {vat:.0%} внутри цены и без входного вычета ориентир для 10 аппаратов поднимается примерно до **{number(ten_vat_green)} л/день на аппарат** даже при OPEX {number(ten_opex)} RSD; налоговая классификация и общий оборот компании требуют подтверждения.",
        "",
        "## Что осталось неизвестным",
        "",
        f"- Фактические литры в день по конкретному адресу, повторные покупки и готовность платить в диапазоне {e['price_test_range_rsd_l']['low']:g}–{e['price_test_range_rsd_l']['high']:g} RSD/л — **нет данных**.",
        f"- Плата за место и коммуникации, сервис, фильтры, анализы, поддержка, бухгалтерия, фискализация — **нет сопоставимых котировок**; OPEX {number(opex)} и переменные {variable:g} RSD/л остаются допущениями.",
        f"- Цена и комплектация аппарата, предельная выдача литров в день, срок службы, остаточная стоимость, стоимость демонтажа — **нет подтверждённой сметы**; CAPEX {number(capex)} и {red_months} месяцев условны.",
        "- Применимый режим НДС для компании и продажи обработанной воды, сумма допустимого входного НДС, налоговая база по прибыли — **нет индивидуального расчёта**. Одна точка по этой модели ниже порога 8 млн RSD, но важен общий оборот компании.",
        "- Снижение затрат в сети, дополнительные центральные расходы и переток покупателей между точками — **нет данных**. Таблица 2/5/10 точек является только чувствительностью к общей бухгалтерии.",
        "- Право на размещение, законная фискальная схема и допуск воды для конкретной точки — **нет подтверждения**; финансовые условия не заменяют право продавать воду.",
        "",
        "Источники налоговых параметров: [Пореска управа — ставка НДС](https://www.purs.gov.rs/pravna-lica/pdv/opste-o-pdv.html), [порог регистрации НДС](https://purs.gov.rs/lat/katalog-usluga.html?position=1), [право на вычет входного НДС](https://www.purs.gov.rs/e-porezi/popdv-uputstvo/polje-8e-1.html), [ставка налога на прибыль](https://www.purs.gov.rs/pravna-lica/pregled-propisa/korisnicka-uputstva/2156/korisnicko-uputstvo-za-primenu-pravilnika-o-sadrzaju-i-nacinu-podnosenja-poreske-prijave-poreza-na-dobit-pravnih-lica.html).",
        "",
    ])
    return ("\n".join(lines)
            .replace("CIT для сравнения", "Условный налог на прибыль для сравнения")
            .replace("условного CIT", "условного налога на прибыль")
            .replace("после CIT", "после налога на прибыль"))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--presentation-output", type=Path, default=DEFAULT_PRESENTATION)
    args = parser.parse_args()
    model = render(json.loads(args.config.read_text(encoding="utf-8")))
    for path in (args.output, args.presentation_output):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(model, encoding="utf-8")


if __name__ == "__main__":
    main()
