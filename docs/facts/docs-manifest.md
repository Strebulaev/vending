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
| README.md | краткий dashboard пилота, главные артефакты и команды | 0001, 0003, 0011, 0042 | docs/plans/integrated-pilot-artifacts-plan.md, docs/project/business-model.md, docs/hardware/, docs/certification/, docs/economics/, config/ | 2026-10-12 |
| docs/README.md | карта пяти артефактов, источников, генераторов и исторических документов | — | структура docs/ | 2026-10-12 |
| docs/project/project-brief.md | исходный brainstorm; не действующая спецификация | 0001–0012 | заменён docs/project/business-model.md и docs/plans/integrated-pilot-artifacts-plan.md | 2026-10-11 |
| docs/project/implementation-plan.md | исторический машинный черновик; не текущий план исполнения | 0001–0012 | заменён docs/plans/integrated-pilot-artifacts-plan.md | 2026-10-11 |
| docs/project/business-model.md | условия возврата вложений, границы отказа и масштабирования пилотного водомата | экономические допущения | config/business-model.json; pipeline/render_business_model.py | 2026-10-12 |
| docs/plans/business-model-dod.md | критерии полноты модели с числовыми границами | экономические допущения | docs/project/business-model.md; config/business-model.json | 2026-10-12 |
| docs/plans/water-vending-configurations-dod.md | критерии готовности типовых конфигураций и спецификаций водоматов для закупки, монтажа и эксплуатации | 0001–0003, 0007–0008, 0020–0025, 0040–0041, 0050–0052, факт 0056 | docs/hardware/, docs/certification/requirements-map.md, docs/economics/ | 2026-10-11 |
| docs/certification/regulatory-inquiry-drafts.md | проекты запросов сербским органам, специалистам и поставщикам; подготовлены, не отправлены | 0001, 0003, 0007, 0011, 0031 | docs/certification/requirements-map.md, docs/hardware/pilot-spec-v1.md | 2026-10-11 |
| docs/project/pilot-launch-guide.md | исторический черновик 2026-10-08; не инструкция к запуску | 0003, 0007, 0008, 0009, 0012, факты 0006, 0009, 0010 | заменён docs/plans/integrated-pilot-artifacts-plan.md и текущими артефактами | 2026-10-11 |
| docs/project/supplier-rfq.md | запрос котировок на аппарат (текст поставщикам на английском) | 0001, 0008, 0012 | docs/hardware/initial-technical-spec.md, docs/project/pilot-launch-guide.md §2 | |
| docs/project/investor-presentation.md | версия условия работы пилота для показа | экономические допущения | config/business-model.json; pipeline/render_business_model.py | 2026-10-12 |
| docs/reports/final-report.md | исторический снимок сводки состояния на 2026-10-09 | 0003, 0011, 0012, 0020–0026, 0030–0033, 0040–0041, 0050–0052 | заменён docs/plans/integrated-pilot-artifacts-plan.md и профильными артефактами | 2026-10-11 |
| docs/reports/problems-and-options.md | исторические проблемы и варианты на 2026-10-09 | 0003, 0011, 0012, 0024, факты 0007, 0009 | заменён docs/plans/integrated-pilot-artifacts-plan.md и профильными артефактами | 2026-10-11 |
| docs/cost-estimates/blocks/*.md | таблицы затрат по блокам (английский) | 0009, 0010, факт 0001 | pipeline/tasks/, pipeline/generator.py, pipeline/fx.py, pipeline/verify.py | |
| docs/cost-estimates/pilot-cost-summary.md | итоговая смета пилота | 0009, факты 0007, 0008 | docs/cost-estimates/blocks/, pipeline/calculator.py | |
| docs/cost-estimates/pilot-scenarios.md | сценарии пилота (генерируется calculator.py) | 0009, факты 0007, 0008 | docs/cost-estimates/blocks/, pipeline/calculator.py | |
| docs/hardware/initial-technical-spec.md | исходное техническое описание RO-300A (v1.2, до решений 0020–0026) | 0002, 0007, факт 0004 | docs/cost-estimates/blocks/TECH.md | |
| docs/hardware/pilot-spec-v1.md | матрица требований и приемки конфигурации пилота | 0001, 0002, 0007, 0008, 0020–0025, 0041, 0050–0052, факты 0010, 0021, 0055 | docs/certification/requirements-map.md, docs/sampling/, RFQ поставщика, docs/hardware/initial-technical-spec.md | 2026-10-11 |
| docs/hardware/specifications/{in-std,in-rei,out-std,out-rei}-v1.md | самостоятельные технические спецификации четырёх конфигураций, генерируемые из общей матрицы и профилей конфигурации | 0001–0008, 0020–0025, 0041, DoD типовых конфигураций | config/equipment-specifications.json, pipeline/build_equipment_specs.py, docs/hardware/pilot-spec-v1.md | 2026-10-11 |
| docs/hardware/machine-configurations.md | варианты IN/OUT × STD/REI, проектный состав, компромиссы и стоимость по найденным позициям | 0007, 0021–0022, 0026, DoD типовых конфигураций | docs/hardware/equipment-cost-estimate.md, docs/plans/water-vending-configurations-dod.md | 2026-10-11 |
| docs/hardware/technical-documentation.md | инженерный черновик схем и полного производственного пакета; не закупочная редакция | 0001–0002, 0007–0008, 0020–0025 | docs/hardware/pilot-spec-v1.md, docs/plans/water-vending-configurations-dod.md, docs/reports/unknowns-and-open-issues.md | 2026-10-11 |
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
| docs/hardware/site-selection-scorecard.md | обязательный фильтр, методика скоринга и паспорт кандидата | 0003, 0011, 0026, факт 0020 | docs/hardware/surcin-candidate-sites.md, docs/hardware/positioning-methodology.md, договор/полевое обследование | 2026-10-11 |
| docs/economics/economics-report.md | итог дорожки «Закупки и экономика» | 0030–0033, факты 0030–0035 | docs/economics/, pipeline/economics.py, pipeline/inventory.py | |
| docs/project/business-model-map.mermaid | архивная схема устройства сервиса; текущая модель её не генерирует | решения 0001–0004, 0011 | docs/project/business-model.md | 2026-10-12 |
| config/business-model.json | финансовые допущения и целевой срок возврата пилотного аппарата | непроверенные входы | docs/project/business-model.md; pipeline/render_business_model.py | 2026-10-12 |
| docs/economics/business-model-calculation.md | параметрический финансовый расчёт точки; не является описанием бизнес-модели, несмотря на старое имя файла | финансовые входы | pipeline/business_model.py; config/business-model-inputs.json; .github/workflows/pilot-unit-economics.yml | 2026-10-12 |
| docs/economics/business-model-flow.mermaid | финансовые формулы, расходы и метрики точки; схема не описывает сам бизнес | финансовая модель | pipeline/business_model.py; .github/workflows/pilot-unit-economics.yml | 2026-10-12 |
| docs/economics/business-model-calculator-guide.md | руководство к параметрическому калькулятору экономики точки (старое имя файла) | финансовые формулы и вводы | config/business-model-inputs.json; pipeline/business_model.py; .github/workflows/pilot-unit-economics.yml | 2026-10-12 |
| docs/process/business-model-and-equipment-runbook.md | операционные шаги обновления, генерации, проверки и выпуска документов бизнес-модели и оборудования | решения владельца; DoD | config/, pipeline/, .github/workflows/ | 2026-10-12 |
| docs/project/github-tour-presentation.md | пошаговая GitHub-презентация пяти артефактов, результатов и ограничений pipeline | текущий контур пилота | README.md, docs/plans/integrated-pilot-artifacts-plan.md, config/, pipeline/, workflows | 2026-10-12 |
| docs/economics/baseline-audit.md | обследование существующей экономики, противоречия, вопросы владельцу | факты 0007, 0009 | pipeline/calculator.py, docs/cost-estimates/pilot-scenarios.md | |
| docs/economics/financial-model.md | сценарии, чувствительность, 1/5/20 точек (генерируется economics.py) | 0032, факты 0007, 0030 | pipeline/economics.py, pipeline/calculator.py | |
| docs/economics/pilot-unit-economics.md | входы, формулы и границы unit economics одной пилотной точки | 0004, 0011, 0030–0033, факты 0003, 0006–0007, 0030, открытые PR/EC/CE/SM вопросы | pipeline/economics.py, docs/reports/unknowns-and-open-issues.md, площадка и котировки | 2026-10-11 |
| docs/economics/pricing.md | бенчмарки, ценовой эксперимент, рекомендация | 0004, 0030, факты 0002, 0009, 0010 | docs/economics/pricing-scenarios.md | |
| docs/economics/pricing-scenarios.md | сценарии цены (генерируется economics.py) | 0004, 0030 | pipeline/economics.py | |
| docs/economics/depreciation-theft-stock.md | амортизация, кража, запас, корпуса | 0032, факт 0034 | pipeline/economics.py, pipeline/inventory.py | |
| docs/economics/ready-made-options-landed-cost.md | цена «от двери до двери» по источникам A/B/D (генерируется economics.py) | 0012, 0031, 0033, факты 0031, 0032, 0035 | pipeline/economics.py, docs/project/supplier-rfq.md | |
| docs/economics/in-house-assembly.md | сборка своими силами: закупки, маршруты, гарантии, приёмка | 0008, 0031, 0033 | docs/hardware/initial-technical-spec.md §9.3 | |
| docs/economics/inventory-model.md | точка заказа, пример с поставкой 8 суток (генерируется inventory.py) | 0032 | pipeline/inventory.py | |
| docs/certification/certification-report.md | итог дорожки «Сертификация» | 0040, 0041, факты 0040–0042 | docs/certification/ | |
| docs/certification/baseline-audit.md | что известно о сертификатах и открытые вопросы | факты 0010, 0040 | docs/project/pilot-launch-guide.md §3.3, §4 | |
| docs/certification/requirements-map.md | карта сертификатов и разрешений по семи областям; «Вне сертификации» | 0040, факты 0040, 0041 | docs/hardware/equipment-cost-estimate.md, официальный PIS, письменные ответы органов | 2026-10-11 |
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
| docs/plans/integrated-pilot-artifacts-plan.md | зависимости и журнал подготовки пяти артефактов пилота | 0001–0012, 0020–0026, 0030–0033, 0040–0041, 0050–0052 | Miro «Сеть водоматов Сербии: треки», пять интегрированных артефактов, открытые вопросы | 2026-10-11 |
| docs/audit/audit-project-and-estimates.md | журнал аудита проектных документов, смет, пайплайна и ранних решений/фактов | 0001–0012, факты 0001–0010 | docs/project/, docs/cost-estimates/, pipeline/ | |
| docs/audit/audit-hardware.md | журнал аудита оборудования | 0020–0026, факты 0020–0021 | docs/hardware/ | |
| docs/audit/audit-economics.md | журнал аудита закупок и экономики | 0030–0033, факты 0030–0035 | docs/economics/, pipeline/economics.py, pipeline/inventory.py | |
| docs/audit/audit-certification.md | журнал аудита сертификации | 0040–0041, факты 0040–0042 | docs/certification/ | |
| docs/audit/audit-sampling.md | журнал аудита отбора проб | 0050–0052, факты 0053–0055 | docs/sampling/, pipeline/sampling_cost.py | |
| docs/reports/unknowns-and-open-issues.md | исторический снимок неизвестных на 2026-10-08; не текущий реестр | все | заменён неизвестными в профильных артефактах и integrated-pilot-artifacts-plan.md | 2026-10-11 |
| docs/archive/README.md | указатель на сохранённые материалы прошлых этапов, не текущие рабочие документы | — | docs/archive/legacy-2026-10/ | 2026-10-11 |
