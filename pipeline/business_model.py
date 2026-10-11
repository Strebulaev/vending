"""Calculate pilot business-model economics from an editable JSON parameter file.

Run: python3 pipeline/business_model.py
Run with workflow/manual overrides: python3 pipeline/business_model.py --overrides-json '{"volume_lpd": 80}'
Unknowns stay unknown; the report lists missing inputs instead of silently treating them as zero.
"""

from __future__ import annotations

import argparse
import copy
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = ROOT / "config" / "business-model-inputs.json"
DEFAULT_OUTPUT = ROOT / "docs" / "economics" / "business-model-calculation.md"
MISSING_ACTIONS = {
    "volume_lpd": ("Маркетинг / пилот", "Измерить литры продаж по дням; до старта провести наблюдение/интервью жителей."),
    "uptime_rate": ("Оборудование / операции", "Запросить SLA поставщика; после запуска считать uptime по журналу простоев."),
    "cashless_revenue_share": ("Финансы / операции", "Измерить долю по фискальным отчетам раздельно для наличных и безналичных продаж."),
    "cashless_order_share": ("Финансы / операции", "Измерить долю транзакций безналичной оплаты; она нужна для расчета числа инкассируемых наличных заказов."),
    "cashless_fee_rate": ("Финансы", "Получить тариф/договор сербского эквайера и платежного модуля."),
    "effective_sales_tax_rate": ("Бухгалтер", "Получить письменную налоговую модель; вводить только эффективный расход на выручку, если так разрешит бухгалтер."),
    "sewer_tariff_rsd_m3": ("Локации / финансы", "Письменно уточнить у BVK категорию и начисление водоотведения для RO-сброса."),
    "sewer_billing_basis": ("Локации / финансы", "Письменно уточнить у BVK, начисляют ли водоотведение по входу, RO-сбросу или объему продукта."),
    "ro_intake_l_per_product_l": ("Оборудование", "Получить гарантию/измерения поставщика и измерить вход/продукт на пилоте."),
    "other_variable_cost_rsd_l": ("Финансы / операции", "Запросить затраты расходников по ресурсу и разделить их на подтвержденный выпуск."),
    "average_order_l": ("Маркетинг / операции", "Измерить литры на транзакцию по фискальным и машинным отчетам."),
    "cash_handling_cost_rsd_per_cash_order": ("Финансы / операции", "Получить стоимость сдачи, обслуживания кассы, возврата и инкассации у поставщика/оператора."),
    "refund_and_failed_sale_cost_rsd_per_order": ("Финансы / операции", "Измерить возвраты и неуспешные транзакции по журналам платежей и автомата."),
    "capex_breakdown.equipment": ("Оборудование / финансы", "Внести стоимость аппарата из сопоставимой письменной котировки."),
    "capex_breakdown.delivery_and_installation": ("Оборудование / финансы", "Внести доставку, монтаж и подключение из письменных предложений."),
    "capex_breakdown.site_preparation": ("Локации / оборудование", "Подтвердить подготовку площадки и коммуникаций осмотром и сметой."),
    "capex_breakdown.permits_and_documentation": ("Юрист / бухгалтер", "Подтвердить обязательные стартовые расходы; правовые требования сверить по карте норм."),
    "capex_breakdown.opening_consumables": ("Операции / качество", "Внести первый комплект фильтров, санитарных средств и проб по котировкам."),
    "monthly_fixed_costs.rent": ("Локации", "Получить письменные коммерческие условия и проект договора."),
    "monthly_fixed_costs.electricity": ("Локации", "Получить расчет электрика/EPS и способ отдельного учета."),
    "monthly_fixed_costs.telemetry_and_connectivity": ("IT", "Получить тарифы связи и платформы для выбранной модели."),
    "monthly_fixed_costs.service_and_filters": ("Оборудование / операции", "Получить сервисный регламент, цены визитов и расходников от поставщика."),
    "monthly_fixed_costs.labor_and_cash_collection": ("Финансы / операции", "Получить график/тариф инкассации и трудозатраты на кассу."),
    "monthly_fixed_costs.laboratory_and_quality": ("Качество", "Подтвердить программу проб и прайс лаборатории для Сурчина."),
    "monthly_fixed_costs.insurance": ("Финансы", "Запросить страховые предложения по уличному аппарату."),
    "monthly_fixed_costs.other": ("Финансы", "Разнести прочие регулярные договорные расходы по подтвержденным счетам."),
    "monthly_fixed_costs.water_readiness_fee": ("Локации / финансы", "Запросить у BVK счет и проверить, является ли погонная готовность отдельной фиксированной строкой."),
    "monthly_fixed_costs.customer_support": ("Операции", "Измерить трудозатраты поддержки пилота и оценить только по фактическому графику/ставке."),
    "monthly_fixed_costs.on_site_labor": ("Операции / финансы", "Указать прямой труд оператора точки по утвержденному графику и ставке; не дублировать инкассацию."),
    "monthly_fixed_costs.local_marketing": ("Маркетинг", "Подтвердить расходы на привлечение жителей по согласованному плану/счетам."),
    "site_area_sqm": ("Локации", "Измерить занимаемую аппаратом площадь при обследовании площадки."),
}

REQUIRED = (
    "price_per_5l_rsd", "volume_lpd", "uptime_rate", "operating_days_month",
    "cashless_revenue_share", "cashless_order_share", "cashless_fee_rate", "effective_sales_tax_rate",
    "water_tariff_rsd_m3", "sewer_tariff_rsd_m3", "sewer_billing_basis", "ro_intake_l_per_product_l",
    "other_variable_cost_rsd_l", "average_order_l", "cash_handling_cost_rsd_per_cash_order",
    "refund_and_failed_sale_cost_rsd_per_order",
)
FIXED_COST_KEYS = (
    "rent", "electricity", "telemetry_and_connectivity", "service_and_filters",
    "labor_and_cash_collection", "laboratory_and_quality", "insurance", "other",
    "water_readiness_fee", "customer_support", "on_site_labor", "local_marketing",
)
CAPEX_KEYS = ("equipment", "delivery_and_installation", "site_preparation", "permits_and_documentation", "opening_consumables")
RATE_KEYS = ("uptime_rate", "cashless_revenue_share", "cashless_order_share", "cashless_fee_rate", "effective_sales_tax_rate")


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def read_inputs(path: Path, overrides_json: str | None) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if overrides_json:
        overrides = json.loads(overrides_json)
        if not isinstance(overrides, dict):
            raise ValueError("Overrides must be a JSON object")
        # Convenience shorthand: a flat JSON object of model inputs is treated as {"inputs": ...}.
        if any(key in REQUIRED or key in ("monthly_fixed_costs", "capex_breakdown") for key in overrides):
            overrides = {"inputs": overrides}
        data = deep_merge(data, overrides)
    return data


def fmt(value: float | None, digits: int = 2) -> str:
    if value is None or not math.isfinite(value):
        return "не рассчитывается"
    return f"{value:,.{digits}f}".replace(",", " ")


def missing_fields(inputs: dict[str, Any]) -> list[str]:
    missing = [key for key in REQUIRED if inputs.get(key) is None]
    capex = inputs.get("capex_breakdown", {})
    missing.extend(f"capex_breakdown.{key}" for key in CAPEX_KEYS if capex.get(key) is None)
    fixed = inputs.get("monthly_fixed_costs", {})
    missing.extend(f"monthly_fixed_costs.{key}" for key in FIXED_COST_KEYS if fixed.get(key) is None)
    return missing


def validate(inputs: dict[str, Any], name: str) -> list[str]:
    errors = []
    for key in REQUIRED:
        value = inputs.get(key)
        if key == "sewer_billing_basis":
            if value is not None and value not in ("intake", "reject", "product"):
                errors.append(f"{name}.{key}: допустимы intake, reject, product или null")
            continue
        if value is not None and (not isinstance(value, (int, float)) or not math.isfinite(value)):
            errors.append(f"{name}.{key}: требуется конечное число или null")
    for key in RATE_KEYS:
        value = inputs.get(key)
        if value is not None and not 0 <= value <= 1:
            errors.append(f"{name}.{key}: доля должна быть в диапазоне 0..1")
    for key in ("price_per_5l_rsd", "operating_days_month", "average_order_l"):
        value = inputs.get(key)
        if value is not None and value <= 0:
            errors.append(f"{name}.{key}: значение должно быть больше нуля")
    if inputs.get("volume_lpd") is not None and inputs["volume_lpd"] < 0:
        errors.append(f"{name}.volume_lpd: объем не может быть отрицательным")
    if inputs.get("ro_intake_l_per_product_l") is not None and inputs["ro_intake_l_per_product_l"] < 1:
        errors.append(f"{name}.ro_intake_l_per_product_l: коэффициент забора должен быть не меньше 1")
    costs = inputs.get("monthly_fixed_costs", {})
    for key in FIXED_COST_KEYS:
        value = costs.get(key)
        if value is not None and (not isinstance(value, (int, float)) or value < 0 or not math.isfinite(value)):
            errors.append(f"{name}.monthly_fixed_costs.{key}: требуется неотрицательное число или null")
    capex = inputs.get("capex_breakdown", {})
    for key in CAPEX_KEYS:
        value = capex.get(key)
        if value is not None and (not isinstance(value, (int, float)) or value < 0 or not math.isfinite(value)):
            errors.append(f"{name}.capex_breakdown.{key}: требуется неотрицательное число или null")
    area = inputs.get("site_area_sqm")
    if area is not None and (not isinstance(area, (int, float)) or not math.isfinite(area) or area <= 0):
        errors.append(f"{name}.site_area_sqm: требуется положительная площадь в м² или null")
    for section, rate_fields in (("customer_metrics", ()), ("market", ("serviceable_share", "obtainable_share"))):
        values = inputs.get(section, {})
        for key, value in values.items():
            if value is not None and (not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0):
                errors.append(f"{name}.{section}.{key}: требуется неотрицательное число или null")
        for key in rate_fields:
            value = values.get(key)
            if value is not None and value > 1:
                errors.append(f"{name}.{section}.{key}: доля должна быть в диапазоне 0..1")
    return errors


def calculate(inputs: dict[str, Any]) -> dict[str, float] | None:
    if missing_fields(inputs):
        return None
    price_l = inputs["price_per_5l_rsd"] / 5
    actual_liters = inputs["volume_lpd"] * inputs["operating_days_month"] * inputs["uptime_rate"]
    revenue = actual_liters * price_l
    cashless_share = inputs["cashless_revenue_share"]
    cashless_fee = revenue * cashless_share * inputs["cashless_fee_rate"]
    tax = revenue * inputs["effective_sales_tax_rate"]
    intake_ratio = inputs["ro_intake_l_per_product_l"]
    sewer_ratio = {"intake": intake_ratio, "reject": intake_ratio - 1, "product": 1}[inputs["sewer_billing_basis"]]
    water_cost = actual_liters * inputs["water_tariff_rsd_m3"] * intake_ratio / 1000
    sewer_cost = actual_liters * inputs["sewer_tariff_rsd_m3"] * sewer_ratio / 1000
    orders = actual_liters / inputs["average_order_l"]
    cash_orders = orders * (1 - inputs["cashless_order_share"])
    cash_cost = cash_orders * inputs["cash_handling_cost_rsd_per_cash_order"]
    refund_cost = orders * inputs["refund_and_failed_sale_cost_rsd_per_order"]
    other_variable = actual_liters * inputs["other_variable_cost_rsd_l"]
    variable_costs = cashless_fee + tax + water_cost + sewer_cost + cash_cost + refund_cost + other_variable
    contribution = revenue - variable_costs
    fixed = sum(inputs["monthly_fixed_costs"].values())
    capex_total = sum(inputs["capex_breakdown"].values())
    operating_result = contribution - fixed
    daily_contribution = (
        price_l * (1 - cashless_share * inputs["cashless_fee_rate"] - inputs["effective_sales_tax_rate"])
        - inputs["ro_intake_l_per_product_l"] * inputs["water_tariff_rsd_m3"] / 1000
        - sewer_ratio * inputs["sewer_tariff_rsd_m3"] / 1000
        - inputs["other_variable_cost_rsd_l"]
        - (1 - inputs["cashless_order_share"]) * inputs["cash_handling_cost_rsd_per_cash_order"] / inputs["average_order_l"]
        - inputs["refund_and_failed_sale_cost_rsd_per_order"] / inputs["average_order_l"]
    )
    effective_open_days = inputs["operating_days_month"] * inputs["uptime_rate"]
    if daily_contribution <= 0:
        break_even_lpd = None
    elif effective_open_days > 0:
        break_even_lpd = fixed / (daily_contribution * effective_open_days)
    else:
        break_even_lpd = None
    payback = capex_total / operating_result if operating_result > 0 else None
    return {
        "price_per_l": price_l,
        "actual_liters_month": actual_liters,
        "revenue_month": revenue,
        "cashless_fee_month": cashless_fee,
        "tax_month": tax,
        "water_cost_month": water_cost,
        "sewer_cost_month": sewer_cost,
        "cash_orders_month": cash_orders,
        "cash_handling_month": cash_cost,
        "refund_cost_month": refund_cost,
        "other_variable_cost_month": other_variable,
        "total_variable_cost_month": variable_costs,
        "contribution_month": contribution,
        "contribution_per_liter": daily_contribution,
        "contribution_per_order": daily_contribution * inputs["average_order_l"],
        "contribution_margin_rate": contribution / revenue if revenue > 0 else None,
        "orders_month": orders,
        "fixed_cost_month": fixed,
        "operating_result_month": operating_result,
        "break_even_lpd": break_even_lpd,
        "break_even_monthly_liters": (break_even_lpd * effective_open_days) if break_even_lpd is not None else None,
        "capex_rsd": capex_total,
        "break_even_orders_month": (break_even_lpd * effective_open_days / inputs["average_order_l"]) if break_even_lpd is not None else None,
        "occupancy_cost_ratio": inputs["monthly_fixed_costs"]["rent"] / revenue if revenue > 0 else None,
        "revenue_per_sqm": (revenue / inputs["site_area_sqm"]) if inputs.get("site_area_sqm") and inputs["site_area_sqm"] > 0 else None,
        "payback_months": payback,
    }


def customer_metrics(data: dict[str, Any], contribution_per_liter: float | None) -> dict[str, Any]:
    cm = data.get("customer_metrics", {})
    required = ("monthly_acquisition_spend_rsd", "new_customers_per_month", "liters_per_customer_month", "customer_lifetime_months")
    missing = [key for key in required if cm.get(key) is None]
    if missing or contribution_per_liter is None:
        return {"missing": missing + (["contribution_per_liter"] if contribution_per_liter is None else [])}
    cac = cm["monthly_acquisition_spend_rsd"] / cm["new_customers_per_month"] if cm["new_customers_per_month"] else None
    ltv = contribution_per_liter * cm["liters_per_customer_month"] * cm["customer_lifetime_months"]
    return {"cac_rsd": cac, "ltv_contribution_rsd": ltv, "ltv_cac_ratio": ltv / cac if cac and cac > 0 else None,
            "cac_payback_months": cac / (contribution_per_liter * cm["liters_per_customer_month"])
            if cac is not None and contribution_per_liter * cm["liters_per_customer_month"] > 0 else None}


def market_metrics(data: dict[str, Any]) -> dict[str, Any]:
    market = data.get("market", {})
    keys = ("eligible_households", "average_household_liters_month", "serviceable_share", "obtainable_share")
    missing = [key for key in keys if market.get(key) is None]
    if missing:
        return {"missing": missing}
    all_liters = market["eligible_households"] * market["average_household_liters_month"]
    sam = all_liters * market["serviceable_share"]
    som = sam * market["obtainable_share"]
    return {"tam_liters_month": all_liters, "sam_liters_month": sam, "som_liters_month": som}


def render(data: dict[str, Any]) -> str:
    base_inputs = deep_merge(data.get("inputs", {}), data.get("scenarios", {}).get("base", {}))
    base_errors = validate(base_inputs, "base")
    base_missing = missing_fields(base_inputs)
    base_calculation = calculate(base_inputs) if not base_errors and not base_missing else None
    if base_calculation is None:
        verdict = "**Финансовый вердикт: данных недостаточно.** Запуск и инвестиционное решение по этой модели не подтверждены."
    elif base_calculation["operating_result_month"] > 0:
        verdict = "**Финансовый вердикт:** положительный операционный денежный результат при введенных входах; решение о запуске требует проверки источников и закрытия правовых/площадочных условий."
    else:
        verdict = "**Финансовый вердикт:** при введенных входах точка не покрывает прямые ежемесячные расходы; закупку/запуск не обосновывает."
    lines = [
        "# Расчет бизнес-модели водомата",
        "",
        f"Сгенерировано `pipeline/business_model.py` из схемы входов v{data.get('meta', {}).get('version', 'не указана')}. Пустые входы остаются «не найдено»; отсутствие значения не трактуется как ноль.",
        "Доля налога ниже — только явно введенная эффективная нагрузка на выручку по заключению бухгалтера; это не утверждение о налоговом режиме Сербии.",
        verdict,
        "",
        "## Сводка сценариев",
        "",
        "| Сценарий | Статус | Выручка/мес., RSD | Результат/мес., RSD | Безубыточность, л/день | Окупаемость CAPEX, мес. |",
        "|---|---|---:|---:|---:|---:|",
    ]
    base = data.get("inputs", {})
    all_results: dict[str, dict[str, Any]] = {}
    scenarios = data.get("scenarios", {})
    for scenario_name in ("downside", "base", "upside"):
        scenario = deep_merge(base, scenarios.get(scenario_name, {}))
        errors = validate(scenario, scenario_name)
        missing = missing_fields(scenario)
        if scenario_name in ("downside", "upside"):
            overrides = scenarios.get(scenario_name, {})
            if not any(overrides.get(key) is not None for key in ("price_per_5l_rsd", "volume_lpd", "uptime_rate", "cashless_revenue_share", "cashless_order_share", "cashless_fee_rate", "sewer_tariff_rsd_m3", "sewer_billing_basis", "ro_intake_l_per_product_l", "other_variable_cost_rsd_l", "monthly_fixed_costs", "capex_breakdown")):
                missing.append("scenario_driver_override")
        result = calculate(scenario) if not errors and not missing else None
        all_results[scenario_name] = {"inputs": scenario, "result": result, "missing": missing, "errors": errors}
        status = "рассчитан" if result else ("ошибка входов" if errors else "неполные входы")
        lines.append("| " + " | ".join((scenario_name, status,
            fmt(result["revenue_month"]) if result else "—",
            fmt(result["operating_result_month"]) if result else "—",
            fmt(result["break_even_lpd"]) if result else "—",
            fmt(result["payback_months"]) if result and result["payback_months"] is not None else "—")) + " |")
    lines.extend(["", "## Источники базовых входов", "", "| Параметр | Значение | Статус источника | Ссылка/пояснение |", "|---|---:|---|---|"])
    sources = data.get("sources", {})
    for key, value in base.items():
        if isinstance(value, dict):
            for subkey, subvalue in value.items():
                full_key = f"{key}.{subkey}"
                source = sources.get(full_key, {})
                shown = fmt(subvalue) if isinstance(subvalue, (int, float)) else subvalue if subvalue is not None else "не найдено"
                lines.append(f"| `{full_key}` | {shown} | {source.get('type', 'источник не указан')} | {source.get('reference', 'добавьте источник/метку сценария')} |")
        else:
            source = sources.get(key, {})
            shown = fmt(value) if isinstance(value, (int, float)) else value if value is not None else "не найдено"
            lines.append(f"| `{key}` | {shown} | {source.get('type', 'источник не указан')} | {source.get('reference', 'добавьте источник/метку сценария')} |")
    for name, item in all_results.items():
        lines.extend(["", f"## {name}", ""])
        if item["errors"]:
            lines.extend(["Ошибки входов:", *[f"- {e}" for e in item["errors"]]])
        elif item["missing"]:
            lines.extend(["Для полного расчёта внесите значения. Пустое значение не заменяется нулём:", "", "| Вход | Роль | Способ закрытия |", "|---|---|---|"])
            for key in item["missing"]:
                if key == "scenario_driver_override":
                    owner, action = ("Владелец модели", "Задать явные отличающиеся драйверы для этого сценария; не копировать базу с ярлыком pessimistic/upside.")
                else:
                    owner, action = MISSING_ACTIONS.get(key, ("Владелец входа", "Сверить источник в реестре открытых вопросов."))
                lines.append(f"| `{key}` | {owner} | {action} |")
        else:
            r = item["result"]
            lines.extend([
                "| Показатель | Значение |",
                "|---|---:|",
                f"| Фактический расчетный объем | {fmt(r['actual_liters_month'])} л/мес. |",
                f"| Цена | {fmt(r['price_per_l'])} RSD/л |",
                f"| Выручка | {fmt(r['revenue_month'])} RSD/мес. |",
                f"| Переменные расходы | {fmt(r['total_variable_cost_month'])} RSD/мес. |",
                f"| Вода и водоотведение | {fmt(r['water_cost_month'] + r['sewer_cost_month'])} RSD/мес. |",
                f"| Наличные: обработка и инкассация | {fmt(r['cash_handling_month'])} RSD/мес. |",
                f"| Возвраты и неуспешные продажи | {fmt(r['refund_cost_month'])} RSD/мес. |",
                f"| Вклад после переменных расходов | {fmt(r['contribution_month'])} RSD/мес. |",
                f"| Вклад на литр | {fmt(r['contribution_per_liter'])} RSD/л |",
                f"| Вклад на средний заказ | {fmt(r['contribution_per_order'])} RSD/заказ |",
                f"| Contribution margin | {fmt(r['contribution_margin_rate'] * 100 if r['contribution_margin_rate'] is not None else None)}% |",
                f"| Заказы | {fmt(r['orders_month'])} заказов/мес. |",
                f"| Постоянные расходы | {fmt(r['fixed_cost_month'])} RSD/мес. |",
                f"| Операционный денежный результат до амортизации | {fmt(r['operating_result_month'])} RSD/мес. |",
                f"| Безубыточность | {fmt(r['break_even_lpd'])} л/день |",
                f"| Безубыточность | {fmt(r['break_even_orders_month'])} заказов/мес. |",
                f"| Аренда / выручка | {fmt(r['occupancy_cost_ratio'] * 100 if r['occupancy_cost_ratio'] is not None else None)}% |",
                f"| Выручка на м² | {fmt(r['revenue_per_sqm'])} RSD/м²/мес. |",
                f"| Полный стартовый CAPEX | {fmt(r['capex_rsd'])} RSD |",
                f"| Окупаемость полного CAPEX | {fmt(r['payback_months'])} мес. |",
            ])
            if r["revenue_per_sqm"] is None:
                owner, action = MISSING_ACTIONS["site_area_sqm"]
                lines.append(f"\nВыручка на м² не рассчитана: `site_area_sqm` не найдено. Ответственный: {owner}; проверка: {action}")
            lines.extend(["", "### Состав CAPEX", "", "| Статья | RSD |", "|---|---:|"])
            for key in CAPEX_KEYS:
                lines.append(f"| `{key}` | {fmt(item['inputs']['capex_breakdown'].get(key))} |")
            projection = data.get("projection", {})
            if projection.get("monthly_volume_growth_rate") is None or projection.get("monthly_fixed_cost_growth_rate") is None:
                lines.append("\n12–36-месячный P&L не строится: внесите темп изменения объема продаж и постоянных расходов с источником/меткой сценария.")
            else:
                months = int(projection.get("months", 12))
                lines.extend(["", f"### P&L по месяцам: {months} мес.", "", "| Месяц | Выручка, RSD | Переменные, RSD | Постоянные, RSD | Операционный результат, RSD |", "|---:|---:|---:|---:|---:|"])
                days = item["inputs"]["operating_days_month"]
                uptime = item["inputs"]["uptime_rate"]
                sales_growth = projection["monthly_volume_growth_rate"]
                cost_growth = projection["monthly_fixed_cost_growth_rate"]
                for month in range(months):
                    factor_sales = (1 + sales_growth) ** month
                    factor_cost = (1 + cost_growth) ** month
                    rev = r["revenue_month"] * factor_sales
                    var = r["total_variable_cost_month"] * factor_sales
                    fixed = r["fixed_cost_month"] * factor_cost
                    lines.append(f"| {month + 1} | {fmt(rev)} | {fmt(var)} | {fmt(fixed)} | {fmt(rev-var-fixed)} |")
    base_result = all_results.get("base", {}).get("result")
    contrib_l = base_result["contribution_per_liter"] if base_result else None
    lines.extend(["", "## CAC / LTV", ""])
    cm = customer_metrics(data, contrib_l)
    if "missing" in cm:
        lines.append("Не рассчитываются; входы не найдены: " + ", ".join(f"`{v}`" for v in cm["missing"]) + ".")
    else:
        lines.extend([f"- CAC: {fmt(cm['cac_rsd'])} RSD; LTV по вкладу: {fmt(cm['ltv_contribution_rsd'])} RSD; LTV/CAC: {fmt(cm['ltv_cac_ratio'])}; возврат CAC: {fmt(cm['cac_payback_months'])} мес."])
    lines.extend(["", "## TAM / SAM / SOM по выбранному catchment", ""])
    mm = market_metrics(data)
    if "missing" in mm:
        lines.append("Не рассчитываются; требуется источник для: " + ", ".join(f"`{v}`" for v in mm["missing"]) + ".")
    else:
        lines.append(f"TAM: {fmt(mm['tam_liters_month'])} л/мес.; SAM: {fmt(mm['sam_liters_month'])} л/мес.; SOM: {fmt(mm['som_liters_month'])} л/мес.")
    lines.extend(["", "## Чувствительность и точки отказа", ""])
    sensitivity = data.get("sensitivity", {})
    swing = sensitivity.get("relative_change")
    if not base_result or swing is None:
        lines.append("Не рассчитана: заполните полный базовый сценарий и `sensitivity.relative_change` (долю изменения для анализа; это параметр анализа, не факт рынка).")
    else:
        drivers = sensitivity.get("parameters", ["price_per_5l_rsd", "volume_lpd", "uptime_rate", "monthly_fixed_costs.rent"])
        lines.extend([f"Относительное изменение: ±{fmt(swing * 100, 1)}% (параметр анализа владельца).", "", "| Драйвер | Низкий ввод: результат / окупаемость | База: результат / окупаемость | Высокий ввод: результат / окупаемость |", "|---|---:|---:|---:|"])
        base_inputs = all_results["base"]["inputs"]
        for driver in drivers:
            low = copy.deepcopy(base_inputs)
            high = copy.deepcopy(base_inputs)
            parts = driver.split(".")
            if len(parts) == 2 and parts[0] == "monthly_fixed_costs":
                key = parts[1]
                if low[parts[0]][key] is None:
                    lines.append(f"| `{driver}` | вход не найден | — | вход не найден |")
                    continue
                low[parts[0]][key] *= 1 - swing
                high[parts[0]][key] *= 1 + swing
            elif driver in low and isinstance(low[driver], (int, float)):
                low[driver] *= 1 - swing
                high[driver] *= 1 + swing
            else:
                lines.append(f"| `{driver}` | вход не распознан | — | вход не распознан |")
                continue
            low_result, high_result = calculate(low), calculate(high)
            low_cell = f"{fmt(low_result['operating_result_month'])} RSD / {fmt(low_result['payback_months'])} мес." if low_result else "—"
            base_cell = f"{fmt(base_result['operating_result_month'])} RSD / {fmt(base_result['payback_months'])} мес."
            high_cell = f"{fmt(high_result['operating_result_month'])} RSD / {fmt(high_result['payback_months'])} мес." if high_result else "—"
            lines.append(f"| `{driver}` | {low_cell} | {base_cell} | {high_cell} |")
        lines.append("\nТочка безубыточности считается по текущему составу расходов; критические правовые/санитарные блокеры являются отдельными no-go условиями.")
    lines.extend(["", "## Интерпретация", "", "- CAC/LTV и TAM/SAM/SOM — условные расчеты из внесённых параметров, не рыночные факты, пока нет источников и наблюдений.",
                  "- Операционный результат не является чистой прибылью и не включает амортизацию, финансирование и не введенные расходы.",
                  "- Unit economics показывает прямую экономику точки; корпоративные/сетевые накладные расходы не включены и должны быть добавлены отдельно перед оценкой прибыли DOO.",
                  "- Полный результат пригоден к решению только если входы подтверждены, применимость налоговой формулы проверена бухгалтером, а бизнес/нормативные блокеры закрыты.",
                  "- Вводы и их источники: `config/business-model-inputs.json`; вопросная база: `docs/reports/unknowns-and-open-issues.md`."])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--overrides-json", default=None, help="JSON object merged into the input document (workflow_dispatch)")
    args = parser.parse_args()
    data = read_inputs(args.input, args.overrides_json)
    projection = data.get("projection", {})
    months = projection.get("months", 12)
    if not isinstance(months, int) or not 12 <= months <= 36:
        raise SystemExit("projection.months должен быть целым числом от 12 до 36")
    swing = data.get("sensitivity", {}).get("relative_change")
    if swing is not None and (not isinstance(swing, (int, float)) or not 0 <= swing <= 1):
        raise SystemExit("sensitivity.relative_change должен быть долей от 0 до 1 или null")
    for key in ("monthly_volume_growth_rate", "monthly_fixed_cost_growth_rate"):
        growth = projection.get(key)
        if growth is not None and (not isinstance(growth, (int, float)) or not math.isfinite(growth) or growth < -1):
            raise SystemExit(f"projection.{key} должен быть конечным числом не меньше -1 или null")
    errors = []
    for name, scenario in data.get("scenarios", {}).items():
        merged = deep_merge(data.get("inputs", {}), scenario)
        errors.extend(validate(merged, name))
    if errors:
        raise SystemExit("\n".join(errors))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(data), encoding="utf-8")
    # Auto-generate mermaid diagram from inputs
    inputs = data.get("inputs", {})
    mermaid_path = ROOT / "docs" / "economics" / "business-model-flow.mermaid"
    mermaid_path.parent.mkdir(parents=True, exist_ok=True)
    mermaid_text = f"""flowchart TD
    subgraph Inputs ["Inputs - auto from pipeline/business_model.py"]
        price["price_per_5l_rsd = {inputs.get('price_per_5l_rsd', 'null')}"]
        vol["volume_lpd = {inputs.get('volume_lpd', 'null')}"]
        upt["uptime_rate = {inputs.get('uptime_rate', 'null')}"]
        days["operating_days_month = {inputs.get('operating_days_month', 'null')}"]
        tariff_w["water_tariff_rsd_m3 = {inputs.get('water_tariff_rsd_m3', 'null')}"]
        tariff_s["sewer_tariff_rsd_m3 = {inputs.get('sewer_tariff_rsd_m3', 'null')}"]
    end
    subgraph Calc ["Calculation: pipeline/business_model.py"]
        calc["Scenarios: downside / base / upside"]
    end
    Inputs --> Calc
    Calc --> Out["Report: docs/economics/business-model-calculation.md"]
    Calc --> Mer["Diagram: docs/economics/business-model-flow.mermaid"]
"""
    mermaid_path.write_text(mermaid_text, encoding="utf-8")
    print(f"Создано: {mermaid_path.relative_to(ROOT) if mermaid_path.is_relative_to(ROOT) else mermaid_path}")
    print(f"Создано: {args.output.relative_to(ROOT) if args.output.is_relative_to(ROOT) else args.output}")
    print("Сценарии:")
    report = render(data)
    print("\n".join(line for line in report.splitlines() if line.startswith("| downside |") or line.startswith("| base |") or line.startswith("| upside |")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
