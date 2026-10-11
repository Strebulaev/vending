# Карта документации

Всё о проекте — в этой папке. Если нужно что-то найти, начните здесь. Имя файла говорит, что в нём: `*-report.md` — итог раздела, `baseline-audit.md` — что было известно до работы и какие там пробелы, остальное — тема файла.

## С чего начать

| Вопрос | Файл |
|---|---|
| Что мы делаем и где что лежит | [../README.md](../README.md) |
| Общий итог: сколько стоит запуск, варианты, сроки, решения владельца | [reports/final-report.md](reports/final-report.md) |
| Какие проблемы есть и как их решать (плюсы, минусы, риски) | [reports/problems-and-options.md](reports/problems-and-options.md) |
| Всё неизвестное («не найдено») и расчёты, которые нельзя исправить | [reports/unknowns-and-open-issues.md](reports/unknowns-and-open-issues.md) |

## Папки

| Папка | Что в ней |
|---|---|
| [project/](project/) | Бизнес-документы: исходный бриф, [бизнес-модель пилота](project/business-model.md), план реализации, руководство по запуску пилота, запрос котировок поставщикам, презентация инвесторам |
| [hardware/](hardware/) | Оборудование: смета по позициям, baseline пилотной спецификации, [четыре спецификации конфигураций](hardware/specifications/), техническая документация, бак и нагрев, модели, телеметрия, позиционирование, [скоринг точек](hardware/site-selection-scorecard.md), типы локаций и кандидаты площадок. Итог — `hardware-report.md` |
| [economics/](economics/) | Закупки и экономика: [юнит-экономика точки](economics/pilot-unit-economics.md), [руководство параметрического калькулятора](economics/business-model-calculator-guide.md), финансовая модель, [расчет бизнес-модели из параметров](economics/business-model-calculation.md), цена, амортизация и кража, цена аппарата «от двери до двери», сборка своими силами, модель запасов. Итог — `economics-report.md` |
| [certification/](certification/) | Сертификация: карта разрешений Сербии, [проекты запросов (не отправлены)](certification/regulatory-inquiry-drafts.md), «покупаем» против «производим», мастер-сертификация, бюджет и сроки. Итог — `certification-report.md` |
| [sampling/](sampling/) | Отбор проб воды: стандартная конфигурация, программа проб, правило выборки, стоимость, логистика. Итог — `sampling-report.md` |
| [cost-estimates/](cost-estimates/) | Сметы: таблицы затрат по блокам (`blocks/`, английский), итоговая смета пилота и сценарии |
| [audit/](audit/) | Журналы аудита 2026-10-08: что проверено по источникам, что исправлено, удалено, помечено как допущение; остающиеся пробелы |
| [plans/](plans/) | Планы работ по дорожкам, включая [DoD бизнес-модели](plans/business-model-dod.md) и [DoD типовых конфигураций водоматов](plans/water-vending-configurations-dod.md) |
| [facts/](facts/), [decisions/](decisions/), [guardrails/](guardrails/), [skills/](skills/) | База знаний: факты, решения, правила, словарь тегов и роли. В каждой папке `INDEX.md`; связь документов с решениями — `facts/docs-manifest.md` |

## Что генерируется скриптами (не править вручную)

| Файл | Скрипт |
|---|---|
| `cost-estimates/pilot-scenarios.md` | `pipeline/calculator.py` |
| `economics/financial-model.md`, `pricing-scenarios.md`, `ready-made-options-landed-cost.md` | `pipeline/economics.py` |
| `economics/business-model-calculation.md` | Исполняемый pipeline `pipeline/business_model.py`; canvas и входы — `config/business-model-inputs.json` |
| `economics/business-model-flow.mermaid` | Исполняемый pipeline `pipeline/business_model.py`, canvas плюс формулы расчетов |
| `hardware/specifications/*-v1.md` | `pipeline/build_equipment_specs.py`, семейство — `config/equipment-specifications.json`, общая матрица — `hardware/pilot-spec-v1.md` |
| `economics/inventory-model.md` | `pipeline/inventory.py` |
| `sampling/program-costs.md` | `pipeline/sampling_cost.py` |

Остальные файлы пишутся вручную.

## Правила

- Язык: сметы в `cost-estimates/blocks/` — английский; всё остальное — русский.
- Имена файлов — латиницей через дефис и по теме; в папке дорожки итоговый файл называется `<дорожка>-report.md`.
- В документах остаются только значения с открытым источником (URL или путь), решения владельца и арифметика по ним; всё остальное — «не найдено» с указанием, кого спросить, и записью в `reports/unknowns-and-open-issues.md`.

## Управление задачами пилота

- [GitHub Issues: DoD пяти артефактов и управление через gh](process/github-issue-management.md)
