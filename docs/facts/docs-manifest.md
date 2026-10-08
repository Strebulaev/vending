---
id: docs-manifest
title: Документы для людей: связь с содержанием, решениями и путями отслеживания дрейфа
status: active
date: 2026-10-08
tags: [documentation]
kind: derived
governed-by: TBD
bootstrap-generated: true
---

| документ / раздел | описывает | решения / факты | отслеживаемые пути | last-verified |
|---|---|---|---|---|
| business_plan/water_vending_brief.md §2 оборудование | требования к аппарату | 0001, 0007, 0008 | тот же файл, docs/technical/TECH_SPEC.md | |
| …brief.md §3 локации | площадки, аудитории | 0003, факт 0006 | тот же файл, presentations/ | |
| …brief.md §4 продукт | качество воды | 0002 | тот же файл, TECH_SPEC.md | |
| …brief.md §5 цены, франшиза | цена, масштаб | 0004, 0005, 0006 | тот же файл | |
| …brief.md §6 финансы, налоги | наличные, разделение налогов | факты 0002, 0003 | тот же файл, pipeline/estimates | |
| business_plan/water_vending_plan.md | поэтапный план, модули | 0001–0012 | brief.md, docs/pipeline/estimates/ | |
| business_plan/pilot_implementation.md | закупка аппарата, договоры, сертификация воды, установка | 0003, 0007, 0008, 0009, 0012, факты 0006, 0009, 0010 | TECH_SPEC.md, pipeline/estimates/{TECH,LEGAL,LOCATIONS}.md | |
| business_plan/rfq_pilot_machine.md | запрос котировок на пилотный аппарат (текст для поставщиков на английском) | 0001, 0008, 0012 | TECH_SPEC.md, pilot_implementation.md §2 | |
| technical/TECH_SPEC.md | RO-300A, очистка, розлив | 0002, 0007, факт 0004 | pipeline/estimates/TECH.md | |
| pipeline/estimates/*.md | таблицы затрат по блокам | 0009, 0010, факт 0001 | pipeline/tasks/, pipeline/generator.py, pipeline/fx.py, pipeline/verify.py | |
| pipeline/consolidated/SMETA_FINAL.md, pilot_scenarios.md | итоговая смета пилота и сценарии | 0009, факты 0007, 0008 | pipeline/estimates/, pipeline/calculator.py | |
| presentations/business_presentation_single_point.md | питч одной точки для инвесторов | 0003, 0004, факты 0004, 0007 | consolidated/SMETA_FINAL.md, pipeline/calculator.py | |
| README.md | цели, текущее состояние, карта репозитория, команды | 0003, 0011, факт 0007 | docs/plans/, pipeline/, docs/pipeline/consolidated/ | |
