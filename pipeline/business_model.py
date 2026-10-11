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
DEFAULT_DIAGRAM = ROOT / "docs" / "economics" / "business-model-flow.mermaid"
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
    "startup_cash_requirements.lease_deposit": ("Локации / финансы", "Подтвердить депозит по проекту договора; если не требуется, внести 0 с ссылкой на условие."),
    "startup_cash_requirements.prepaid_rent": ("Локации / финансы", "Подтвердить авансовый период и сумму аренды по договору."),
    "startup_cash_requirements.cash_float_for_change": ("Финансы / операции", "Рассчитать начальный разменный фонд по кассете, номиналам, лимитам и графику инкассации."),
    "startup_cash_requirements.opening_working_capital": ("Финансы", "Определить резерв оборотного капитала из условий расчетов, сроков оплаты, закупки расходников и возвратов."),
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
STARTUP_CASH_KEYS = ("lease_deposit", "prepaid_rent", "cash_float_for_change", "opening_working_capital")
RATE_KEYS = ("uptime_rate", "cashless_revenue_share", "cashless_order_share", "cashless_fee_rate", "effective_sales_tax_rate")
NONNEGATIVE_KEYS = ("water_tariff_rsd_m3", "sewer_tariff_rsd_m3", "other_variable_cost_rsd_l", "cash_handling_cost_rsd_per_cash_order", "refund_and_failed_sale_cost_rsd_per_order")


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def read_inputs(path: Path, overrides_json: str | None, overrides_file: Path | None = None) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Не удалось прочитать JSON входов {path}: {exc}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("inputs"), dict):
        raise ValueError("Файл входов должен быть JSON-объектом с объектом `inputs`")
    raw_override = overrides_json
    if overrides_file is not None:
        try:
            raw_override = overrides_file.read_text(encoding="utf-8")
        except OSError as exc:
            raise ValueError(f"Не удалось прочитать файл параметров {overrides_file}: {exc}") from exc
    if raw_override and raw_override.strip() not in ("", "{}"):
        try:
            overrides = json.loads(raw_override)
        except json.JSONDecodeError as exc:
            raise ValueError(f"JSON параметров некорректен (строка {exc.lineno}, столбец {exc.colno}): {exc.msg}") from exc
        if not isinstance(overrides, dict):
            raise ValueError("Overrides must be a JSON object")
        # Convenience shorthand: a flat JSON object of model inputs is treated as {"inputs": ...}.
        if any(key in REQUIRED or key in ("monthly_fixed_costs", "capex_breakdown", "startup_cash_requirements", "site_area_sqm") for key in overrides):
            overrides = {"inputs": overrides}
        data = deep_merge(data, overrides)
    if not isinstance(data.get("inputs"), dict):
        raise ValueError("В объединенных параметрах `inputs` должен быть JSON-объектом")
    return data


def fmt(value: float | None, digits: int = 2) -> str:
    if value is None or not math.isfinite(value):
        return "не рассчитывается"
    return f"{value:,.{digits}f}".replace(",", " ")


def missing_fields(inputs: dict[str, Any]) -> list[str]:
    missing = [key for key in REQUIRED if inputs.get(key) is None]
    capex = inputs.get("capex_breakdown", {})
    if not isinstance(capex, dict):
        capex = {}
    missing.extend(f"capex_breakdown.{key}" for key in CAPEX_KEYS if capex.get(key) is None)
    startup_cash = inputs.get("startup_cash_requirements", {})
    if not isinstance(startup_cash, dict):
        startup_cash = {}
    missing.extend(f"startup_cash_requirements.{key}" for key in STARTUP_CASH_KEYS if startup_cash.get(key) is None)
    fixed = inputs.get("monthly_fixed_costs", {})
    if not isinstance(fixed, dict):
        fixed = {}
    missing.extend(f"monthly_fixed_costs.{key}" for key in FIXED_COST_KEYS if fixed.get(key) is None)
    return missing


def has_scenario_driver(overrides: dict[str, Any]) -> bool:
    for key, value in overrides.items():
        if key in ("monthly_fixed_costs", "capex_breakdown", "startup_cash_requirements") and isinstance(value, dict):
            if any(item is not None for item in value.values()):
                return True
        elif value is not None:
            return True
    return False


def validate(inputs: dict[str, Any], name: str) -> list[str]:
    errors = []
    allowed_input_keys = set(REQUIRED) | {"monthly_fixed_costs", "capex_breakdown", "startup_cash_requirements", "site_area_sqm"}
    unknown = sorted(set(inputs) - allowed_input_keys)
    if unknown:
        errors.append(f"{name}: неизвестные поля inputs: {', '.join(unknown)}")
    for key in REQUIRED:
        value = inputs.get(key)
        if key == "sewer_billing_basis":
            if value is not None and value not in ("intake", "reject", "product"):
                errors.append(f"{name}.{key}: допустимы intake, reject, product или null")
            continue
        if value is not None and (type(value) not in (int, float) or not math.isfinite(value)):
            errors.append(f"{name}.{key}: требуется конечное число или null")
    for key in RATE_KEYS:
        value = inputs.get(key)
        if value is not None and type(value) in (int, float) and not 0 <= value <= 1:
            errors.append(f"{name}.{key}: доля должна быть в диапазоне 0..1")
    for key in ("price_per_5l_rsd", "operating_days_month", "average_order_l"):
        value = inputs.get(key)
        if value is not None and type(value) in (int, float) and value <= 0:
            errors.append(f"{name}.{key}: значение должно быть больше нуля")
    for key in NONNEGATIVE_KEYS:
        value = inputs.get(key)
        if type(value) in (int, float) and value < 0:
            errors.append(f"{name}.{key}: значение не может быть отрицательным")
    if type(inputs.get("volume_lpd")) in (int, float) and inputs["volume_lpd"] < 0:
        errors.append(f"{name}.volume_lpd: объем не может быть отрицательным")
    if type(inputs.get("ro_intake_l_per_product_l")) in (int, float) and inputs["ro_intake_l_per_product_l"] < 1:
        errors.append(f"{name}.ro_intake_l_per_product_l: коэффициент забора должен быть не меньше 1")
    costs = inputs.get("monthly_fixed_costs", {})
    if not isinstance(costs, dict):
        errors.append(f"{name}.monthly_fixed_costs: требуется JSON-объект")
        costs = {}
    extra_fixed = sorted(set(costs) - set(FIXED_COST_KEYS))
    if extra_fixed:
        errors.append(f"{name}.monthly_fixed_costs: неизвестные статьи: {', '.join(extra_fixed)}")
    for key in FIXED_COST_KEYS:
        value = costs.get(key)
        if value is not None and (type(value) not in (int, float) or value < 0 or not math.isfinite(value)):
            errors.append(f"{name}.monthly_fixed_costs.{key}: требуется неотрицательное число или null")
    capex = inputs.get("capex_breakdown", {})
    if not isinstance(capex, dict):
        errors.append(f"{name}.capex_breakdown: требуется JSON-объект")
        capex = {}
    extra_capex = sorted(set(capex) - set(CAPEX_KEYS))
    if extra_capex:
        errors.append(f"{name}.capex_breakdown: неизвестные статьи: {', '.join(extra_capex)}")
    for key in CAPEX_KEYS:
        value = capex.get(key)
        if value is not None and (type(value) not in (int, float) or value < 0 or not math.isfinite(value)):
            errors.append(f"{name}.capex_breakdown.{key}: требуется неотрицательное число или null")
    startup_cash = inputs.get("startup_cash_requirements", {})
    if not isinstance(startup_cash, dict):
        errors.append(f"{name}.startup_cash_requirements: требуется JSON-объект")
        startup_cash = {}
    extra_startup_cash = sorted(set(startup_cash) - set(STARTUP_CASH_KEYS))
    if extra_startup_cash:
        errors.append(f"{name}.startup_cash_requirements: неизвестные статьи: {', '.join(extra_startup_cash)}")
    for key in STARTUP_CASH_KEYS:
        value = startup_cash.get(key)
        if value is not None and (type(value) not in (int, float) or value < 0 or not math.isfinite(value)):
            errors.append(f"{name}.startup_cash_requirements.{key}: требуется неотрицательное число или null")
    area = inputs.get("site_area_sqm")
    if area is not None and (type(area) not in (int, float) or not math.isfinite(area) or area <= 0):
        errors.append(f"{name}.site_area_sqm: требуется положительная площадь в м² или null")
    for section, rate_fields in (("customer_metrics", ()), ("market", ("serviceable_share", "obtainable_share"))):
        values = inputs.get(section, {})
        if not isinstance(values, dict):
            errors.append(f"{name}.{section}: требуется JSON-объект")
            continue
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
    startup_cash = sum(inputs["startup_cash_requirements"].values())
    total_initial_cash = capex_total + startup_cash
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
    payback_capex = capex_total / operating_result if operating_result > 0 else None
    payback_total = total_initial_cash / operating_result if operating_result > 0 else None
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
        "startup_cash_rsd": startup_cash,
        "total_initial_cash_rsd": total_initial_cash,
        "break_even_orders_month": (break_even_lpd * effective_open_days / inputs["average_order_l"]) if break_even_lpd is not None else None,
        "occupancy_cost_ratio": inputs["monthly_fixed_costs"]["rent"] / revenue if revenue > 0 else None,
        "revenue_per_sqm": (revenue / inputs["site_area_sqm"]) if inputs.get("site_area_sqm") and inputs["site_area_sqm"] > 0 else None,
        "payback_capex_months": payback_capex,
        "payback_months": payback_total,
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


def business_model_diagram() -> str:
    """Pipeline-level business and calculation map embedded in reports and exported for GitHub."""
    return """flowchart TD
    subgraph Drivers["1. Входные параметры и подтверждения"]
        Demand["Спрос: литры в день V"]
        Uptime["Доступность: uptime u"]
        Days["Рабочие дни: D"]
        Price["Цена: p RSD/л"]
        Orders["Средний заказ: л/чек"]
        Area["Площадь точки, м² (если измерена)"]
        PaymentShares["Оплата: доля cashless-выручки и доля cashless-чеков"]
        WaterParams["Вода: тариф, RO коэффициент k, база тарифа канализации"]
        CostInputs["Переменные ставки и прямые расходы точки"]
        CapexInputs["CAPEX: аппарат + доставка/монтаж + площадка + документы + пусковые материалы"]
        StartupCashInputs["Стартовый cash: депозит + предоплата + разменный фонд + оборотный резерв"]
    end

    subgraph Canvas["0. Операционная бизнес-модель из config/business-model-inputs.json"]
        Segment["Клиентский сегмент и задача клиента"]
        ValueOffer["Ценность: RO-вода в тару клиента"]
        SalesChannel["Точка продаж: уличный водомат 24/7"]
        Operator["Оператор: DOO; самообслуживание"]
        ActivitySet["Активности: закупка, подключение, контроль воды, обслуживание, учет"]
        PartnerSet["Площадка, поставщик, коммунальные и платежные партнеры, лаборатория"]
        RevenueModel["Выручка: цена × проданные литры"]
        CostModel["Затраты: CAPEX + переменные + прямые фиксированные"]
        PilotGate["Гейт масштабирования: из решения 0011"]
        Segment --> ValueOffer --> SalesChannel --> RevenueModel
        Operator --> ActivitySet --> SalesChannel
        PartnerSet --> ActivitySet
        CostModel --> FourWallResult
        PilotGate --> Verdict
    end

    subgraph Sales["2. Объем продаж и выручка"]
        Liters["Проданные литры L = V × D × u"]
        TicketCount["Количество заказов N = L / средний заказ"]
        Revenue["Выручка = L × p"]
        Liters --> TicketCount
        Liters --> Revenue
    end

    subgraph VariableCosts["3. Переменные расходы и contribution"]
        WaterCost["Водоснабжение = L × k × тариф воды / 1000"]
        SewerCost["Водоотведение = L × коэффициент базы × тариф / 1000"]
        CardCost["Эквайринг = cashless-выручка × комиссия"]
        TaxCost["Эффективный расход с выручки по заключению бухгалтера"]
        CashCost["Наличные = cash-заказы × стоимость обработки/инкассации"]
        RefundCost["Возвраты/сбои = заказы × стоимость на заказ"]
        OtherVariable["Другие подтвержденные переменные расходы"]
        VariableTotal["Все переменные расходы"]
        Contribution["Contribution = выручка − переменные расходы"]
        WaterCost --> VariableTotal
        SewerCost --> VariableTotal
        CardCost --> VariableTotal
        TaxCost --> VariableTotal
        CashCost --> VariableTotal
        RefundCost --> VariableTotal
        OtherVariable --> VariableTotal
        Revenue --> Contribution
        VariableTotal --> Contribution
    end

    subgraph FourWall["4. Прямые постоянные расходы точки — four-wall"]
        Rent["Аренда площадки"]
        Fixed["Аренда + коммунальные + сервис/фильтры + связь + труд/инкассация + лаборатория + страховка + поддержка + локальный маркетинг + прочее"]
        FourWallResult["Результат точки до амортизации и финансирования = contribution − four-wall"]
        Contribution --> FourWallResult
        Fixed --> FourWallResult
        Rent --> Fixed
    end

    subgraph DecisionMetrics["5. Метрики и инвестиционное решение"]
        UnitMetrics["Вклад/л и вклад/заказ; contribution margin"]
        BreakEven["BEP: литры/день и заказы/месяц"]
        CapexTotal["Полный стартовый CAPEX"]
        StartupCashTotal["Первоначальная потребность = CAPEX + стартовый cash"]
        Payback["Срок возврата CAPEX / положительный результат точки"]
        FullCashPayback["Срок возврата всех первоначально вложенных средств"]
        SiteMetrics["Аренда / выручка; выручка / площадь точки"]
        Gate["Отдельные go/no-go: правовой допуск, вода/качество, договор площадки, утвержденный лимит владельца"]
        Verdict["Вердикт: данных недостаточно / расходы не покрыты / положительная экономика по введенным данным"]
        Contribution --> UnitMetrics
        FourWallResult --> BreakEven
        Fixed --> BreakEven
        FourWallResult --> Payback
        CapexInputs --> CapexTotal
        CapexTotal --> Payback
        CapexTotal --> StartupCashTotal
        StartupCashInputs --> StartupCashTotal
        StartupCashTotal --> FullCashPayback
        FourWallResult --> FullCashPayback
        Revenue --> SiteMetrics
        Rent --> SiteMetrics
        Area --> SiteMetrics
        UnitMetrics --> BreakEven
        Payback --> Verdict
        FullCashPayback --> Verdict
        BreakEven --> Verdict
        Gate --> Verdict
    end

    subgraph Extensions["6. Дополнительный анализ — только при наличии данных"]
        Scenarios["Downside / base / upside: явно заданные драйверы сценариев"]
        Sensitivity["Чувствительность: 2–3 выбранных драйвера и диапазон изменения"]
        PnL["Операционный прогноз точки на 12–36 месяцев"]
        Customer["CAC / LTV: расходы привлечения, новые клиенты, литры/клиент, срок жизни"]
        Catchment["TAM / SAM / SOM: домохозяйства × литры/домохозяйство × подтвержденные доли"]
        NetworkOH["Корпоративные/сетевые расходы не входят в unit economics точки"]
    end

    Demand --> Liters
    Uptime --> Liters
    Days --> Liters
    Price --> Revenue
    Orders --> TicketCount
    PaymentShares --> CardCost
    PaymentShares --> CashCost
    WaterParams --> WaterCost
    WaterParams --> SewerCost
    CostInputs --> CardCost
    CostInputs --> TaxCost
    CostInputs --> CashCost
    CostInputs --> RefundCost
    CostInputs --> OtherVariable
    CostInputs --> Fixed
    Drivers --> Scenarios
    Scenarios --> Liters
    Scenarios --> FourWallResult
    FourWallResult --> Sensitivity
    FourWallResult --> PnL
    UnitMetrics --> Customer
    Demand --> Catchment
    Liters --> WaterCost
    Liters --> SewerCost
    TicketCount --> CashCost
    TicketCount --> RefundCost

    classDef input fill:#eaf2f8,stroke:#2874a6,color:#17202a
    classDef cost fill:#fdebd0,stroke:#ca6f1e,color:#17202a
    classDef calc fill:#e8f8f5,stroke:#148f77,color:#17202a
    classDef decision fill:#f5eef8,stroke:#7d3c98,color:#17202a
    class Demand,Uptime,Days,Price,Orders,Area,PaymentShares,WaterParams,CostInputs,CapexInputs,StartupCashInputs input
    class WaterCost,SewerCost,CardCost,TaxCost,CashCost,RefundCost,OtherVariable,VariableTotal,Rent,Fixed cost
    class Liters,TicketCount,Revenue,Contribution,UnitMetrics,BreakEven,CapexTotal,StartupCashTotal,Payback,FullCashPayback,SiteMetrics calc
    class FourWallResult,Gate,Verdict decision
    class Scenarios,Sensitivity,PnL,Customer,Catchment,NetworkOH decision
"""


def model_canvas(data: dict[str, Any]) -> dict[str, Any]:
    """Return the structured business model that drives the generated output."""
    return data.get("business_model", {})


def pipeline_stages(data: dict[str, Any]) -> list[dict[str, Any]]:
    base = deep_merge(data.get("inputs", {}), data.get("scenarios", {}).get("base", {}))
    missing = missing_fields(base)
    result = calculate(base) if not missing else None
    customer = customer_metrics(data, result["contribution_per_liter"] if result else None)
    market = market_metrics(data)
    scenarios = data.get("scenarios", {})
    scenario_complete = True
    for name in ("downside", "base", "upside"):
        inputs = deep_merge(data.get("inputs", {}), scenarios.get(name, {}))
        if missing_fields(inputs) or validate(inputs, name) or (name != "base" and not has_scenario_driver(scenarios.get(name, {}))):
            scenario_complete = False
    customer_status = "calculated" if not customer.get("missing") else "incomplete"
    return [
        {"stage": "validate_configuration", "status": "passed"},
        {"stage": "assemble_business_model_canvas", "status": "passed", "fields": len(model_canvas(data))},
        {"stage": "calculate_unit_economics", "status": "passed" if not missing else "incomplete", "missing_inputs": missing},
        {"stage": "market_sizing", "status": "calculated" if not market.get("missing") else "incomplete", "missing_inputs": market.get("missing", [])},
        {"stage": "customer_economics", "status": customer_status, "missing_inputs": customer.get("missing", [])},
        {"stage": "scenario_analysis", "status": "calculated" if scenario_complete else "incomplete"},
        {"stage": "sensitivity_analysis", "status": "calculated" if result and data.get("sensitivity", {}).get("relative_change") is not None else "incomplete"},
        {"stage": "launch_decision", "status": "requires_external_clearances", "gate_sources": ["docs/certification/requirements-map.md", "docs/hardware/site-selection-scorecard.md", "docs/decisions/0011-pilot-gate.md"]},
        {"stage": "publish_reproducible_package", "status": "ready", "outputs": ["Markdown report", "Mermaid diagram", "JSON results"]},
    ]


def render_canvas(data: dict[str, Any]) -> list[str]:
    canvas = model_canvas(data)
    labels = {
        "legal_form": "Оператор и юридическая форма",
        "customer_segment": "Клиентский сегмент",
        "job_to_be_done": "Задача клиента / JTBD",
        "value_proposition": "Ценностное предложение",
        "sales_channel": "Канал и место продаж",
        "payment_and_revenue": "Монетизация и оплата",
        "customer_relationship": "Отношения и поддержка клиента",
        "key_activities": "Ключевые активности",
        "key_resources": "Ключевые ресурсы",
        "key_partners": "Ключевые партнеры",
        "cost_structure": "Структура затрат",
        "scale_gate": "Гейт пилота и масштабирования",
    }
    lines = ["## Структурная бизнес-модель", "", "Эти поля загружаются из конфигурации и проходят тот же pipeline, что расчеты. Статус показывает, решение это, гипотеза или неизвестное.", "", "| Блок модели | Формулировка | Статус | Источник |", "|---|---|---|---|"]
    for key, label in labels.items():
        item = canvas.get(key, {})
        value = str(item.get("value") or "не найдено").replace("|", "\\|").replace("\n", " ")
        source = str(item.get("source") or "не найдено").replace("|", "\\|")
        lines.append(f"| {label} | {value} | {item.get('status', 'не указан')} | `{source}` |")
    return lines


def render(data: dict[str, Any]) -> str:
    base_inputs = deep_merge(data.get("inputs", {}), data.get("scenarios", {}).get("base", {}))
    base_errors = validate(base_inputs, "base")
    base_missing = missing_fields(base_inputs)
    base_calculation = calculate(base_inputs) if not base_errors and not base_missing else None
    if base_calculation is None:
        verdict = f"**Финансовый вердикт: данных недостаточно.** Не заполнено обязательных полей: {len(base_missing)}. Запуск и инвестиционное решение по этой модели не подтверждены."
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
        "## Стадии pipeline",
        "",
        "| Этап | Статус | Детали |",
        "|---|---|---|",
        *[
            f"| `{stage['stage']}` | {stage['status']} | {', '.join(stage.get('missing_inputs', stage.get('gate_sources', stage.get('outputs', [])))) or str(stage.get('fields', '—'))} |"
            for stage in pipeline_stages(data)
        ],
        "",
        *render_canvas(data),
        "",
        "## Сводка сценариев",
        "",
        "| Сценарий | Статус | Выручка/мес., RSD | Результат/мес., RSD | Безубыточность, л/день | Возврат стартовых вложений, мес. |",
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
            if not has_scenario_driver(overrides):
                missing.append("scenario_driver_override")
        result = calculate(scenario) if not errors and not missing else None
        all_results[scenario_name] = {"inputs": scenario, "result": result, "missing": missing, "errors": errors}
        status = "рассчитан" if result else ("ошибка входов" if errors else "неполные входы")
        lines.append("| " + " | ".join((scenario_name, status,
            fmt(result["revenue_month"]) if result else "—",
            fmt(result["operating_result_month"]) if result else "—",
            fmt(result["break_even_lpd"]) if result else "—",
            fmt(result["payback_months"]) if result and result["payback_months"] is not None else "—")) + " |")
    lines.extend(["", "## Как считается модель", "", "```mermaid", business_model_diagram().rstrip(), "```", "",
                  "Диаграмма показывает формулы и зависимости. Финансовые значения приведены ниже; пустые параметры не заменяются нулями.",
        "", "## Реестр параметров и источников", "", "| Параметр | Значение | Статус источника | Ссылка/пояснение |", "|---|---:|---|---|"])
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
    for section in ("customer_metrics", "market", "projection", "sensitivity"):
        values = data.get(section, {})
        for key, value in values.items():
            full_key = f"{section}.{key}"
            source = sources.get(full_key, {})
            shown = fmt(value) if isinstance(value, (int, float)) else value if value is not None else "не найдено"
            lines.append(f"| `{full_key}` | {shown} | {source.get('type', 'источник не указан')} | {source.get('reference', 'добавьте источник/метку сценария')} |")
    for scenario_name in ("downside", "base", "upside"):
        scenario = data.get("scenarios", {}).get(scenario_name, {})
        for key, value in scenario.items():
            nested_values = value.items() if isinstance(value, dict) else ((None, value),)
            for subkey, subvalue in nested_values:
                input_key = f"{key}.{subkey}" if subkey is not None else key
                scoped_source = sources.get(f"scenarios.{scenario_name}.{input_key}", sources.get(input_key, {}))
                shown = fmt(subvalue) if isinstance(subvalue, (int, float)) else subvalue if subvalue is not None else "не найдено"
                lines.append(f"| `scenarios.{scenario_name}.{input_key}` | {shown} | {scoped_source.get('type', 'источник не указан')} | {scoped_source.get('reference', 'добавьте источник/метку сценария')} |")
    common_missing = [key for key in all_results.get("base", {}).get("missing", []) if key != "scenario_driver_override"]
    if common_missing:
        lines.extend(["", "## Обязательные неизвестные базовой экономики", "", "| Параметр | Ответственная роль | Как закрыть |", "|---|---|---|"])
        for key in common_missing:
            owner, action = MISSING_ACTIONS.get(key, ("Владелец входа", "Сверить значение и основание в первичном источнике."))
            lines.append(f"| `{key}` | {owner} | {action} |")
    optional_rows = []
    if base.get("site_area_sqm") is None:
        optional_rows.append(("Выручка/м²", *MISSING_ACTIONS["site_area_sqm"]))
    if any(value is None for value in data.get("customer_metrics", {}).values()):
        optional_rows.append(("CAC / LTV", "Маркетинг / финансы", "После пилота оценить возможность агрегированного учета привлечения, уникальных клиентов и повторных покупок; не подменять неизвестную атрибуцию предположением."))
    if any(value is None for value in data.get("market", {}).values()):
        optional_rows.append(("TAM / SAM / SOM", "Маркетинг / локации", "Для конкретного catchment собрать источник числа домохозяйств и измеренную потребность; доли SAM/SOM обосновать доступностью и пилотной конверсией."))
    if data.get("projection", {}).get("monthly_volume_growth_rate") is None or data.get("projection", {}).get("monthly_fixed_cost_growth_rate") is None:
        optional_rows.append(("Операционный прогноз точки на 12–36 месяцев", "Финансы / владелец модели", "Сначала получить фактическую базу; прогнозные темпы продаж и затрат задать как явный сценарий с источником, не использовать как факт."))
    if data.get("sensitivity", {}).get("relative_change") is None:
        optional_rows.append(("Чувствительность", "Владелец модели", "Выбрать диапазон изменения для 2–3 драйверов; это настройка анализа, не рыночное значение."))
    if optional_rows:
        lines.extend(["", "## Необязательные модули — не блокируют расчет одной точки", "", "| Модуль | Ответственная роль | Как закрыть |", "|---|---|---|"])
        for module, owner, action in optional_rows:
            lines.append(f"| {module} | {owner} | {action} |")
    for name, item in all_results.items():
        lines.extend(["", f"## {name}", ""])
        if item["errors"]:
            lines.extend(["Ошибки входов:", *[f"- {e}" for e in item["errors"]]])
        elif item["missing"]:
            scenario_only = [key for key in item["missing"] if key not in common_missing]
            lines.append("Расчёт не выполнен: заполните обязательные неизвестные из реестра выше; пустые значения не считаются нулём.")
            if scenario_only:
                lines.extend(["", "Сценарные входы:", "", "| Вход | Ответственная роль | Как закрыть |", "|---|---|---|"])
                for key in scenario_only:
                    if key == "scenario_driver_override":
                        owner, action = ("Владелец модели", "Задать отличающийся драйвер из сценарного диапазона/явного предположения с источником.")
                    else:
                        owner, action = MISSING_ACTIONS.get(key, ("Владелец входа", "Сверить значение и основание в первичном источнике."))
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
                f"| Депозит, предоплата, размен и оборотный резерв | {fmt(r['startup_cash_rsd'])} RSD |",
                f"| Всего требуется при запуске | {fmt(r['total_initial_cash_rsd'])} RSD |",
                f"| Возврат CAPEX | {fmt(r['payback_capex_months'])} мес. |",
                f"| Возврат всех первоначальных вложений | {fmt(r['payback_months'])} мес. |",
            ])
            if r["revenue_per_sqm"] is None:
                owner, action = MISSING_ACTIONS["site_area_sqm"]
                lines.append(f"\nВыручка на м² не рассчитана: `site_area_sqm` не найдено. Ответственный: {owner}; проверка: {action}")
            lines.extend(["", "### Состав CAPEX", "", "| Статья | RSD |", "|---|---:|"])
            for key in CAPEX_KEYS:
                lines.append(f"| `{key}` | {fmt(item['inputs']['capex_breakdown'].get(key))} |")
            lines.extend(["", "### Стартовая потребность в денежных средствах", "", "| Статья | RSD |", "|---|---:|"])
            for key in STARTUP_CASH_KEYS:
                lines.append(f"| `{key}` | {fmt(item['inputs']['startup_cash_requirements'].get(key))} |")
            projection = data.get("projection", {})
            if projection.get("monthly_volume_growth_rate") is None or projection.get("monthly_fixed_cost_growth_rate") is None:
                lines.append("\nОперационный прогноз точки на 12–36 месяцев не строится: внесите темп изменения объема продаж и постоянных расходов с источником/меткой сценария.")
            else:
                months = int(projection.get("months", 12))
                lines.extend(["", f"### Операционный прогноз точки по месяцам: {months} мес.", "", "Показывает выручку, переменные и прямые постоянные расходы точки и операционный результат до амортизации, финансирования и налога на прибыль. Не является полным P&L или прогнозом чистой прибыли.", "", "| Месяц | Выручка, RSD | Переменные, RSD | Постоянные, RSD | Операционный результат, RSD |", "|---:|---:|---:|---:|---:|---:|"])
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
        lines.append("Не рассчитана: заполните полный базовый сценарий и `sensitivity.relative_change`. Ответственный — владелец модели; это выбранный диапазон анализа, а не факт рынка.")
    else:
        drivers = sensitivity.get("parameters", ["price_per_5l_rsd", "volume_lpd", "uptime_rate"])
        lines.extend([f"Относительное изменение: ±{fmt(swing * 100, 1)}% (параметр анализа владельца).", "", "| Драйвер | Низкий ввод: результат / окупаемость | База: результат / окупаемость | Высокий ввод: результат / окупаемость |", "|---|---:|---:|---:|"])
        base_inputs = all_results["base"]["inputs"]
        for driver in drivers:
            low = copy.deepcopy(base_inputs)
            high = copy.deepcopy(base_inputs)
            parts = driver.split(".")
            if len(parts) == 2 and parts[0] in ("monthly_fixed_costs", "capex_breakdown", "startup_cash_requirements"):
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
    parser.add_argument("--diagram-output", type=Path, default=DEFAULT_DIAGRAM)
    parser.add_argument("--json-output", type=Path, default=None, help="Optional machine-readable resolved inputs and scenario results")
    parser.add_argument("--overrides-json", default=None, help="JSON object merged into the input document (workflow_dispatch)")
    parser.add_argument("--overrides-file", type=Path, default=None, help="JSON file merged into the input document")
    args = parser.parse_args()
    if args.overrides_json is not None and args.overrides_file is not None:
        parser.error("Используйте только один из параметров --overrides-json и --overrides-file")
    try:
        data = read_inputs(args.input, args.overrides_json, args.overrides_file)
    except ValueError as exc:
        parser.error(str(exc))
    for section in ("sources", "scenarios", "customer_metrics", "market", "projection", "sensitivity"):
        if not isinstance(data.get(section, {}), dict):
            parser.error(f"{section} должен быть JSON-объектом")
    canvas = data.get("business_model", {})
    expected_canvas = ("legal_form", "customer_segment", "job_to_be_done", "value_proposition", "sales_channel", "payment_and_revenue", "customer_relationship", "key_activities", "key_resources", "key_partners", "cost_structure", "scale_gate")
    if not isinstance(canvas, dict):
        parser.error("business_model должен быть JSON-объектом")
    canvas_errors = []
    for key in expected_canvas:
        item = canvas.get(key)
        if not isinstance(item, dict):
            canvas_errors.append(f"business_model.{key}: требуется объект value/status/source")
        elif not all(isinstance(item.get(field), str) and item[field].strip() for field in ("value", "status", "source")):
            canvas_errors.append(f"business_model.{key}: value, status и source обязательны")
    if canvas_errors:
        parser.error("\n".join(canvas_errors))
    projection = data.get("projection", {})
    months = projection.get("months", 12)
    if type(months) is not int or not 12 <= months <= 36:
        raise SystemExit("projection.months должен быть целым числом от 12 до 36")
    swing = data.get("sensitivity", {}).get("relative_change")
    if swing is not None and (type(swing) not in (int, float) or not math.isfinite(swing) or not 0 <= swing <= 1):
        raise SystemExit("sensitivity.relative_change должен быть долей от 0 до 1 или null")
    for key in ("monthly_volume_growth_rate", "monthly_fixed_cost_growth_rate"):
        growth = projection.get(key)
        if growth is not None and (type(growth) not in (int, float) or not math.isfinite(growth) or growth < -1):
            raise SystemExit(f"projection.{key} должен быть конечным числом не меньше -1 или null")
    scenarios = data.get("scenarios", {})
    unknown_scenarios = sorted(set(scenarios) - {"downside", "base", "upside"})
    if unknown_scenarios:
        parser.error("Неизвестные сценарии: " + ", ".join(unknown_scenarios))
    for name, scenario in scenarios.items():
        if not isinstance(scenario, dict):
            parser.error(f"scenarios.{name} должен быть JSON-объектом")
    errors = []
    errors.extend(validate(data["inputs"], "inputs"))
    for name, scenario in scenarios.items():
        merged = deep_merge(data.get("inputs", {}), scenario)
        errors.extend(validate(merged, name))
    for section, fields in (("customer_metrics", ("monthly_acquisition_spend_rsd", "new_customers_per_month", "liters_per_customer_month", "customer_lifetime_months")),
                            ("market", ("eligible_households", "average_household_liters_month", "serviceable_share", "obtainable_share"))):
        values = data.get(section, {})
        unknown = sorted(set(values) - set(fields))
        if unknown:
            errors.append(f"{section}: неизвестные поля: {', '.join(unknown)}")
        for key, value in values.items():
            if value is not None and (type(value) not in (int, float) or not math.isfinite(value) or value < 0):
                errors.append(f"{section}.{key}: требуется неотрицательное конечное число или null")
        for key in (("serviceable_share", "obtainable_share") if section == "market" else ()):
            value = values.get(key)
            if value is not None and value > 1:
                errors.append(f"{section}.{key}: доля должна быть в диапазоне 0..1")
    sensitivity = data.get("sensitivity", {})
    drivers = sensitivity.get("parameters", [])
    numeric_drivers = {"price_per_5l_rsd", "volume_lpd", "uptime_rate", "cashless_revenue_share", "cashless_order_share", "cashless_fee_rate", "effective_sales_tax_rate", "water_tariff_rsd_m3", "sewer_tariff_rsd_m3", "ro_intake_l_per_product_l", "other_variable_cost_rsd_l", "average_order_l", "cash_handling_cost_rsd_per_cash_order", "refund_and_failed_sale_cost_rsd_per_order"}
    allowed_drivers = numeric_drivers | {f"monthly_fixed_costs.{key}" for key in FIXED_COST_KEYS} | {f"capex_breakdown.{key}" for key in CAPEX_KEYS} | {f"startup_cash_requirements.{key}" for key in STARTUP_CASH_KEYS}
    if not isinstance(drivers, list) or any(not isinstance(driver, str) or driver not in allowed_drivers for driver in drivers):
        errors.append("sensitivity.parameters: используйте список допустимых полей модели")
    elif not 2 <= len(drivers) <= 3:
        errors.append("sensitivity.parameters: задайте 2 или 3 ключевых драйвера")
    for key, source in data.get("sources", {}).items():
        if not isinstance(source, dict):
            errors.append(f"sources.{key}: источник должен быть объектом с type/reference")
    if errors:
        raise SystemExit("\n".join(errors))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.diagram_output.parent.mkdir(parents=True, exist_ok=True)
    report = render(data)
    args.output.write_text(report, encoding="utf-8")
    diagram = business_model_diagram()
    args.diagram_output.write_text(diagram, encoding="utf-8")
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        result_payload = {"meta": data.get("meta", {}), "business_model": model_canvas(data), "inputs": data["inputs"], "sources": data.get("sources", {}),
                          "customer_metrics": data.get("customer_metrics", {}), "market": data.get("market", {}),
                          "projection": projection, "sensitivity": data.get("sensitivity", {}),
                          "pipeline": {"stages": pipeline_stages(data)}, "scenarios": {}}
        for name in ("downside", "base", "upside"):
            scenario_inputs = deep_merge(data["inputs"], scenarios.get(name, {}))
            scenario_errors = validate(scenario_inputs, name)
            scenario_missing = missing_fields(scenario_inputs)
            if name in ("downside", "upside") and not has_scenario_driver(scenarios.get(name, {})):
                scenario_missing.append("scenario_driver_override")
            result_payload["scenarios"][name] = {
                "status": "calculated" if not scenario_errors and not scenario_missing else "incomplete" if not scenario_errors else "invalid",
                "missing": scenario_missing,
                "errors": scenario_errors,
                "inputs": scenario_inputs,
                "result": calculate(scenario_inputs) if not scenario_errors and not scenario_missing else None,
            }
        args.json_output.write_text(json.dumps(result_payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        print(f"Создано: {args.json_output.relative_to(ROOT) if args.json_output.is_relative_to(ROOT) else args.json_output}")
    print(f"Создано: {args.diagram_output.relative_to(ROOT) if args.diagram_output.is_relative_to(ROOT) else args.diagram_output}")
    print(f"Создано: {args.output.relative_to(ROOT) if args.output.is_relative_to(ROOT) else args.output}")
    print("Сценарии:")
    print("\n".join(line for line in report.splitlines() if line.startswith("| downside |") or line.startswith("| base |") or line.startswith("| upside |")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
