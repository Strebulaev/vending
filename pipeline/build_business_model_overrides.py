"""Merge GitHub workflow form fields and advanced JSON into model overrides."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


FORM_FIELDS = {
    "price_per_5l_rsd", "volume_lpd", "uptime_rate", "operating_days_month",
    "cashless_revenue_share", "cashless_order_share", "cashless_fee_rate",
    "effective_sales_tax_rate", "water_tariff_rsd_m3", "sewer_tariff_rsd_m3",
    "sewer_billing_basis", "ro_intake_l_per_product_l", "other_variable_cost_rsd_l",
    "average_order_l", "cash_handling_cost_rsd_per_cash_order",
    "refund_and_failed_sale_cost_rsd_per_order", "site_area_sqm",
}
FIXED_FIELDS = {
    "monthly_fixed_costs_rent": "rent",
    "monthly_fixed_costs_electricity": "electricity",
    "monthly_fixed_costs_telemetry_and_connectivity": "telemetry_and_connectivity",
    "monthly_fixed_costs_service_and_filters": "service_and_filters",
    "monthly_fixed_costs_labor_and_cash_collection": "labor_and_cash_collection",
    "monthly_fixed_costs_laboratory_and_quality": "laboratory_and_quality",
    "monthly_fixed_costs_insurance": "insurance",
}
ENVELOPE_KEYS = {"inputs", "sources", "scenarios", "customer_metrics", "market", "projection", "sensitivity", "meta"}


def parse_form_value(name: str, raw_value: object) -> object:
    value = str(raw_value).strip()
    if value.lower() == "null":
        return None
    if name == "sewer_billing_basis":
        return value
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{name}: введите число или null") from exc
    if parsed is not None and type(parsed) not in (int, float):
        raise ValueError(f"{name}: ожидается число или null")
    return parsed


def build(raw: object) -> tuple[dict, int, list[str]]:
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        raise ValueError("GitHub workflow inputs должны быть JSON-объектом")
    raw = dict(raw)
    advanced_text = raw.pop("parameters_json", "") or ""
    if not isinstance(advanced_text, str):
        raise ValueError("parameters_json должен быть строкой с JSON-объектом")
    try:
        advanced = json.loads(advanced_text) if advanced_text.strip() else {}
    except json.JSONDecodeError as exc:
        raise ValueError(f"parameters_json: ошибка JSON в строке {exc.lineno}, столбце {exc.colno}: {exc.msg}") from exc
    if not isinstance(advanced, dict):
        raise ValueError("parameters_json должен содержать JSON-объект")
    if advanced and not (set(advanced) & ENVELOPE_KEYS):
        advanced = {"inputs": advanced}
    overrides = advanced
    overrides.setdefault("inputs", {})
    if not isinstance(overrides["inputs"], dict):
        raise ValueError("parameters_json.inputs должен быть JSON-объектом")

    manual_inputs: dict[str, object] = {}
    manual_fixed: dict[str, object] = {}
    unknown_form_fields = set(raw) - FORM_FIELDS - set(FIXED_FIELDS)
    if unknown_form_fields:
        raise ValueError("Неизвестные поля формы: " + ", ".join(sorted(unknown_form_fields)))
    for name, raw_value in raw.items():
        if raw_value is None or not str(raw_value).strip():
            continue
        if name in FORM_FIELDS:
            manual_inputs[name] = parse_form_value(name, raw_value)
        else:
            fixed_name = FIXED_FIELDS[name]
            manual_fixed[fixed_name] = parse_form_value(name, raw_value)

    # Form fields win over JSON overrides; an empty form field leaves JSON/config intact.
    overrides["inputs"].update(manual_inputs)
    if manual_fixed:
        monthly = overrides["inputs"].setdefault("monthly_fixed_costs", {})
        if not isinstance(monthly, dict):
            raise ValueError("parameters_json.inputs.monthly_fixed_costs должен быть JSON-объектом")
        monthly.update(manual_fixed)
    if manual_inputs or manual_fixed:
        sources = overrides.setdefault("sources", {})
        if not isinstance(sources, dict):
            raise ValueError("parameters_json.sources должен быть JSON-объектом")
        for name in manual_inputs:
            sources[name] = {
                "type": "workflow_manual_input",
                "reference": "Введено вручную в GitHub Actions; добавьте договор, счет, замер или решение владельца для подтверждения.",
            }
        for name in manual_fixed:
            sources[f"monthly_fixed_costs.{name}"] = {
                "type": "workflow_manual_input",
                "reference": "Введено вручную в GitHub Actions; добавьте договор, счет, замер или решение владельца для подтверждения.",
            }
    return overrides, len(manual_inputs) + len(manual_fixed), sorted(set(overrides) - {"inputs"})


def main() -> int:
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/overrides.json")
    try:
        raw = json.loads(os.environ.get("DISPATCH_INPUTS_JSON") or "{}")
        overrides, manual_count, advanced_sections = build(raw)
    except (json.JSONDecodeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(overrides, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Сохранены overrides: {output}")
    print(f"Параметров из формы: {manual_count}; секции JSON: {', '.join(advanced_sections) or 'нет'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
