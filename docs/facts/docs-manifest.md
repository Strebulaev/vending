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

Все пути от корня репозитория. Столбец «отслеживаемые пути» — что должно измениться, чтобы документ устарел.

| документ | описывает | решения / факты | отслеживаемые пути | last-verified |
|---|---|---|---|---|
| README.md | цели, текущее состояние, карта репозитория, команды | 0003, 0011, факт 0007 | docs/README.md, pipeline/ | |
| docs/README.md | карта документации | — | структура docs/ | |
| docs/project/project-brief.md | исходные требования и открытые вопросы (§2 оборудование, §3 локации, §4 продукт, §5 цены, §6 финансы) | 0001, 0002, 0003, 0004, 0005, 0007, 0008, факты 0002, 0003, 0006 | docs/hardware/initial-technical-spec.md, docs/cost-estimates/blocks/ | |
| docs/project/implementation-plan.md | поэтапный план реализации | 0001–0012 | docs/project/project-brief.md, docs/cost-estimates/blocks/ | |
| docs/project/pilot-launch-guide.md | закупка аппарата, договоры, сертификация воды, установка | 0003, 0007, 0008, 0009, 0012, факты 0006, 0009, 0010 | docs/hardware/initial-technical-spec.md, docs/cost-estimates/blocks/{TECH,LEGAL,LOCATIONS}.md | |
| docs/project/supplier-rfq.md | запрос котировок на аппарат (текст поставщикам на английском) | 0001, 0008, 0012 | docs/hardware/initial-technical-spec.md, docs/project/pilot-launch-guide.md §2 | |
| docs/project/investor-presentation.md | питч одной точки для инвесторов (финансы устарели) | 0003, 0004, факты 0004, 0007 | docs/cost-estimates/pilot-cost-summary.md, pipeline/calculator.py | |
| docs/reports/final-report.md | сводный итог четырёх дорожек: смета запуска, варианты, сроки, решения владельца | 0003, 0011, 0012, 0020–0026, 0030–0033, 0040–0041, 0050–0052 | docs/{hardware,economics,certification,sampling}/*-report.md | |
| docs/reports/problems-and-options.md | проблемы пилота и варианты решения с плюсами, минусами, рисками | 0003, 0011, 0012, 0024, факты 0007, 0009 | docs/reports/final-report.md, docs/{economics,sampling}/ | |
| docs/cost-estimates/blocks/*.md | таблицы затрат по блокам (английский) | 0009, 0010, факт 0001 | pipeline/tasks/, pipeline/generator.py, pipeline/fx.py, pipeline/verify.py | |
| docs/cost-estimates/pilot-cost-summary.md | итоговая смета пилота | 0009, факты 0007, 0008 | docs/cost-estimates/blocks/, pipeline/calculator.py | |
| docs/cost-estimates/pilot-scenarios.md | сценарии пилота (генерируется calculator.py) | 0009, факты 0007, 0008 | docs/cost-estimates/blocks/, pipeline/calculator.py | |
| docs/hardware/initial-technical-spec.md | исходное техническое описание RO-300A (v1.2, до решений 0020–0026) | 0002, 0007, факт 0004 | docs/cost-estimates/blocks/TECH.md | |
| docs/hardware/hardware-report.md | итог дорожки «Оборудование» | 0020–0026 | docs/hardware/ | |
| docs/hardware/baseline-audit.md | расхождения источников об оборудовании | 0020–0026 | docs/hardware/equipment-cost-estimate.md | |
| docs/hardware/equipment-cost-estimate.md | смета всего оборудования по позициям и моделям | 0012, 0020–0024, факт 0004 | docs/cost-estimates/blocks/TECH.md, docs/hardware/initial-technical-spec.md | |
| docs/hardware/technical-documentation.md | производственный пакет: схемы, жгуты, прошивка, регламент, приёмка | 0007, 0020–0025, факт 0021 | docs/hardware/initial-technical-spec.md, docs/hardware/equipment-cost-estimate.md | |
| docs/hardware/tank-and-heating.md | малый бак, УФ, слив; обогрев по моделям | 0020, 0021, факт 0021 | docs/hardware/initial-technical-spec.md §2, §7 | |
| docs/hardware/machine-configurations.md | четыре модели, атрибуты, компромиссы, правило усиления | 0007, 0022 | docs/hardware/equipment-cost-estimate.md | |
| docs/hardware/telemetry.md | что собирать, матрица инцидентов, приватность | 0011, 0023, 0024, правило no-dispensing-on-hygiene-alarm | docs/hardware/initial-technical-spec.md §6 | |
| docs/hardware/positioning-methodology.md | позиционирование: метод A (тип локации) и метод B (размещение) | 0003, 0004, 0026, факт 0020 | docs/hardware/location-types.md | |
| docs/hardware/location-types.md | типы локаций и пороги безубыточности | 0003, 0026, факты 0006, 0007, 0020 | docs/cost-estimates/pilot-scenarios.md | |
| docs/hardware/surcin-candidate-sites.md | кандидаты на площадки в Сурчине | 0003, 0026, факт 0020 | docs/hardware/location-types.md | |
| docs/economics/economics-report.md | итог дорожки «Закупки и экономика» | 0030–0033, факты 0030–0035 | docs/economics/, pipeline/economics.py, pipeline/inventory.py | |
| docs/economics/baseline-audit.md | обследование существующей экономики, противоречия, вопросы владельцу | факты 0007, 0009 | pipeline/calculator.py, docs/cost-estimates/pilot-scenarios.md | |
| docs/economics/financial-model.md | сценарии, чувствительность, 1/5/20 точек (генерируется economics.py) | 0032, факты 0007, 0030 | pipeline/economics.py, pipeline/calculator.py | |
| docs/economics/pricing.md | бенчмарки, ценовой эксперимент, рекомендация | 0004, 0030, факты 0002, 0009, 0010 | docs/economics/pricing-scenarios.md | |
| docs/economics/pricing-scenarios.md | сценарии цены (генерируется economics.py) | 0004, 0030 | pipeline/economics.py | |
| docs/economics/depreciation-theft-stock.md | амортизация, кража, запас, корпуса | 0032, факт 0034 | pipeline/economics.py, pipeline/inventory.py | |
| docs/economics/ready-made-options-landed-cost.md | цена «от двери до двери» по источникам A/B/D (генерируется economics.py) | 0012, 0031, 0033, факты 0031, 0032, 0035 | pipeline/economics.py, docs/project/supplier-rfq.md | |
| docs/economics/in-house-assembly.md | сборка своими силами: закупки, маршруты, гарантии, приёмка | 0008, 0031, 0033 | docs/hardware/initial-technical-spec.md §9.3 | |
| docs/economics/inventory-model.md | точка заказа, пример с поставкой 8 суток (генерируется inventory.py) | 0032 | pipeline/inventory.py | |
| docs/certification/certification-report.md | итог дорожки «Сертификация» | 0040, 0041, факты 0040–0042 | docs/certification/ | |
| docs/certification/baseline-audit.md | что известно о сертификатах и открытые вопросы | факты 0010, 0040 | docs/project/pilot-launch-guide.md §3.3, §4 | |
| docs/certification/requirements-map.md | карта сертификатов и разрешений по семи областям; «Вне сертификации» | 0040, факты 0040, 0041 | docs/hardware/equipment-cost-estimate.md | |
| docs/certification/buy-vs-make.md | пути «покупаем» и «производим» для сертификации | 0012, 0040 | docs/project/supplier-rfq.md, docs/certification/requirements-map.md | |
| docs/certification/master-certification.md | мастер-сертификация стандартной конфигурации и правила изменений | 0041 | docs/certification/requirements-map.md, docs/certification/buy-vs-make.md | |
| docs/certification/costs-and-timeline.md | бюджет, сроки, чек-лист «Допуск к запуску» | 0040, факт 0042, правило no-launch-without-clearance-package | docs/certification/buy-vs-make.md | |
| docs/sampling/sampling-report.md | итог дорожки «Отбор проб» | 0050–0052, факты 0053–0055 | docs/sampling/, pipeline/sampling_cost.py | |
| docs/sampling/baseline-audit.md | нормы воды, лаборатории, неизвестное | факты 0053, 0054 | docs/project/pilot-launch-guide.md §4 | |
| docs/sampling/standard-configuration.md | условная стандартная конфигурация STD-1 и точки отбора | 0050, факт 0055 | docs/hardware/machine-configurations.md, docs/hardware/tank-and-heating.md | |
| docs/sampling/sampling-program.md | этапы, показатели, частота, объём пробы, тара | 0050, факты 0053, 0055 | docs/sampling/standard-configuration.md | |
| docs/sampling/scaling-rule.md | правило выборки для N точек | 0051, 0052 | docs/sampling/sampling-program.md | |
| docs/sampling/program-costs.md | стоимость программы проб (генерируется sampling_cost.py) | 0050, 0051, факт 0054 | pipeline/sampling_cost.py | |
| docs/sampling/logistics-lead-time.md | сроки доставки проб и закупки тары, график на 20 точек | 0050, 0051, факт 0055 | docs/economics/inventory-model.md | |
| docs/plans/hardware-track-plan.md | план дорожки «Оборудование» (выполнен) | 0020–0026 | docs/hardware/ | |
| docs/plans/economics-track-plan.md | план дорожки «Закупки и экономика» (выполнен) | 0030–0033 | docs/economics/ | |
| docs/plans/certification-track-plan.md | план дорожки «Сертификация» (выполнен) | 0040, 0041 | docs/certification/ | |
| docs/plans/sampling-track-plan.md | план дорожки «Отбор проб» (выполнен) | 0050–0052 | docs/sampling/ | |
