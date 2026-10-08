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
| hardware/equipment_estimate.md | смета всего оборудования по позициям и моделям | 0012, 0020–0024, факт 0004 | pipeline/estimates/TECH.md, TECH_SPEC.md | |
| hardware/technical_documentation.md | производственный пакет: схемы, жгуты, прошивка, регламент, приёмка | 0007, 0020–0025, факт 0021 | technical/TECH_SPEC.md | |
| hardware/tank_and_heating.md | малый бак, УФ, слив; обогрев по моделям | 0020, 0021, факт 0021 | TECH_SPEC.md §2, §7 | |
| hardware/configurations.md | четыре модели, атрибуты, компромиссы, правило усиления | 0007, 0022 | equipment_estimate.md | |
| hardware/telemetry.md | что собирать, матрица инцидентов, приватность | 0011, 0023, 0024, guardrail no-dispensing-on-hygiene-alarm | TECH_SPEC.md §6 | |
| hardware/positioning_methodology.md | позиционирование: метод A и метод B | 0003, 0004, 0026, факт 0020 | locations.md | |
| hardware/locations.md | типы локаций и пороги безубыточности | 0003, 0026, факты 0006, 0007, 0020 | pipeline/consolidated/pilot_scenarios.md | |
| hardware/surcin_candidates.md | кандидаты на площадки в Сурчине | 0003, 0026, факт 0020 | locations.md | |
| hardware/REPORT.md, findings.md | итог дорожки «Оборудование» и расхождения источников | 0020–0026 | docs/hardware/ | |
| certification/findings.md | что известно о сертификатах и открытые вопросы | факты 0010, 0040 | business_plan/pilot_implementation.md §3.3, §4; TECH_SPEC.md §11.3 | |
| certification/landscape.md | карта сертификатов и разрешений по семи областям; «Вне сертификации» | 0040, факты 0040, 0041, 0010 | TECH_SPEC.md §9.3; официальные акты Sl. glasnik | |
| certification/make_vs_buy.md | пути «покупаем» и «производим» для сертификации | 0012, 0040 | business_plan/rfq_pilot_machine.md; landscape.md | |
| certification/master_certification.md | мастер-сертификация стандартной конфигурации и правила изменений | 0041 | landscape.md, make_vs_buy.md; docs/hardware/configurations.md (ожидает дорожку hardware) | |
| certification/costs_timeline.md | бюджет, сроки, чек-лист «Допуск к запуску» | 0040, факт 0042, правило no-launch-without-clearance-package | make_vs_buy.md, master_certification.md | |
| certification/REPORT.md | итоговый отчёт дорожки сертификации | 0040, 0041, факты 0040–0042 | docs/certification/*.md | |
