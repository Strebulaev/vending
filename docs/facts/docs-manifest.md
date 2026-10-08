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
| business_plan/smeta.md | устаревшая смета (legacy, помечена) | факты 0001, 0007 | docs/pipeline/estimates/ | |
| business_plan/pilot_implementation.md | закупка аппарата, договоры, сертификация воды, установка | 0003, 0007, 0008, 0009, 0012, факты 0006, 0009, 0010 | TECH_SPEC.md, pipeline/estimates/{TECH,LEGAL,LOCATIONS}.md | |
| technical/TECH_SPEC.md | RO-300A, очистка, розлив | 0002, 0007, факт 0004 | pipeline/estimates/TECH.md | |
| technical/PRESENTATION.md | техническая презентация (не просмотрена) | факт 0004 | TECH_SPEC.md | |
| pipeline/estimates/*.md | таблицы затрат по блокам | 0009, 0010, факт 0001 | pipeline/tasks/, pipeline/generator.py, pipeline/fx.py | |
| pipeline/consolidated/*.md | сводные отчёты (частично вручную) | 0009, факты 0007, 0008 | pipeline/estimates/, pipeline/consolidator.py, pipeline/calculator.py | |
| pipeline/reviews/*.md | результаты проверки блоков | 0009 | pipeline/reviewer.py, pipeline/estimates/ | |
| presentations/business_presentation_single_point.md | питч одной точки для инвесторов | 0003, 0004, факты 0004, 0007 | consolidated/summary.md, pipeline/calculator.py | |
