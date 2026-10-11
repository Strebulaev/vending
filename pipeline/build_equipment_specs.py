#!/usr/bin/env python3
"""Generate a standalone equipment specification for every canonical configuration."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "config/equipment-specifications.json"


def render_spec(baseline: str, spec: dict[str, str]) -> str:
    content = baseline.replace("# Спецификация водомата пилота v1", f"# Техническая спецификация оборудования {spec['id']} v1", 1)
    content = content.replace("Этот файл служит источником общей матрицы требований и профиля пилота. Самостоятельные спецификации семейства генерируются в `docs/hardware/specifications/` из `config/equipment-specifications.json` и этой матрицы; результат не следует редактировать вручную.\n", "")
    content = re.sub(r"\*\*Версия:\*\*.*", "**Версия:** 1.0, сгенерировано из конфигурации спецификаций", content, count=1)
    content = re.sub(r"\*\*Конфигурация:\*\*.*", f"**Конфигурация:** `{spec['id']}` — {spec['title']}", content, count=1)
    content = re.sub(r"\*\*Статус:\*\*.*", "**Статус:** техническая базовая спецификация; серийная модель и подтверждения поставщика не выбраны. Не является разрешением на закупку или эксплуатацию.", content, count=1)
    scope = (
        f"Профиль исполнения: **{spec['environment']}**. Защита: **{spec['security']}**.\n\n"
        f"Состав модулей: {spec['modules']}.\n\n"
        f"Статус применения: {spec['use_status']}. Идентификатор конфигурации описывает требования, а не конкретную модель или подтверждённый BOM."
    )
    content = re.sub(r"## Границы конфигурации\n.*?(?=\n## Матрица требований и приемки)",
                     "## Границы конфигурации\n\n" + scope + "\n", content, count=1, flags=re.S)
    # Make the environmental row configuration-neutral; exact site ranges remain a supplier and field-check input.
    lines = []
    for line in content.splitlines():
        if line.startswith("| ENV-01 |"):
            line = ("| ENV-01 | Исполнение оборудования должно соответствовать профилю среды этой конфигурации и измеренным условиям точки; климатические и защитные пределы фиксируются по модели поставщика и обследованию | "
                    f"Решения 0021–0022; профиль {spec['id']}; {spec['source']} | {spec['acceptance']} | {spec['unknowns']} |")
        lines.append(line)
    content = "\n".join(lines)
    content = content.replace("Уличное размещение, доступ 24/7 и схема монтажа", "Соответствие исполнения условиям размещения и схема монтажа")
    config_section = [
        "## Требования профиля конфигурации",
        "",
        "| Параметр | Требование / статус | Источник |",
        "|---|---|---|",
        f"| Среда | {spec['environment']} | `{spec['source']}` |",
        f"| Защита | {spec['security']} | `{spec['source']}` |",
        f"| Модули исполнения | {spec['modules']} | `{spec['source']}` |",
        f"| Критерий применимости | {spec['use_status']} | `{spec['source']}` |",
        f"| Доказательство приемки профиля | {spec['acceptance']} | RFQ поставщика и обследование площадки |",
        f"| Открытые параметры | {spec['unknowns']} | Реестр неизвестных и письменные доказательства |",
        "",
        "Поставщик заполняет эту спецификацию для точной модели. Общие требования ниже применяются дополнительно к этому профилю; при конфликте требуется зафиксировать отклонение и оценить влияние по решению 0041.",
        "",
    ]
    marker = "## Матрица требований и приемки"
    content = content.replace(marker, "\n".join(config_section) + "\n" + marker, 1)
    content = content.replace("# Техническая спецификация оборудования", "# Техническая спецификация оборудования", 1)
    content = content.replace("[Исходная техническая спецификация](initial-technical-spec.md)", "[Исходная техническая спецификация](../initial-technical-spec.md)")
    content = content.replace("[телеметрия](telemetry.md)", "[телеметрия](../telemetry.md)")
    content = content.replace("[мастер-сертификация](../certification/master-certification.md)", "[мастер-сертификация](../../certification/master-certification.md)")
    content = content.replace("[карта норм](../certification/requirements-map.md)", "[карта норм](../../certification/requirements-map.md)")
    content = content.replace("[бизнес-модель](../project/business-model.md)", "[бизнес-модель](../../project/business-model.md)")
    content = content.replace("[скоринг точек](site-selection-scorecard.md)", "[скоринг точек](../site-selection-scorecard.md)")
    siblings = ", ".join(f"[`{item}`]({item.lower()}-v1.md)" for item in ("IN-STD", "IN-REI", "OUT-STD", "OUT-REI") if item != spec["id"])
    content = content.replace("## Связанные материалы", f"## Спецификации семейства\n\n{siblings}.\n\n## Связанные материалы", 1)
    return content.rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, help="Write generated files here; defaults to configured documentation folder")
    parser.add_argument("--check", action="store_true", help="Fail if checked-in generated specs differ from current sources")
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    specs = config.get("specifications")
    required_ids = {"IN-STD", "IN-REI", "OUT-STD", "OUT-REI"}
    if not isinstance(specs, list) or {item.get("id") for item in specs if isinstance(item, dict)} != required_ids:
        parser.error("В конфигурации должны присутствовать ровно IN-STD, IN-REI, OUT-STD и OUT-REI")
    required_fields = {"id", "title", "environment", "security", "modules", "use_status", "source", "acceptance", "unknowns"}
    for item in specs:
        if not isinstance(item, dict) or not required_fields.issubset(item) or not all(isinstance(item[key], str) and item[key].strip() for key in required_fields):
            parser.error("Каждый профиль должен содержать непустые текстовые поля: " + ", ".join(sorted(required_fields)))
    source = ROOT / config["source_baseline"]
    baseline = source.read_text(encoding="utf-8")
    output_dir = args.output_dir or ROOT / config["output_directory"]
    expected: dict[Path, str] = {}
    for spec in config["specifications"]:
        expected[output_dir / f"{spec['id'].lower()}-v1.md"] = render_spec(baseline, spec)
    stale = []
    for path, content in expected.items():
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != content:
                stale.append(str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            print(f"Generated: {path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}")
    if stale:
        print("Generated specifications are stale: " + ", ".join(stale), file=sys.stderr)
        return 1
    if args.check:
        print(f"Verified {len(expected)} equipment specifications are current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
