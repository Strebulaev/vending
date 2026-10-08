# Сценарии пилотной точки

Расчёт `pipeline/calculator.py` для одного жилого аппарата, только безналичная оплата (решения 0001, 0003, 0005, 0011). Каждая строка смет классифицирована в `SCOPE`; исключения и причины — в разделе 6.

## 1. Единовременные затраты: оборудование и установка

| Блок | RSD | EUR |
|------|-----|-----|
| TECH | 308,880 | 2,640 |
| LOCATIONS | 81,900 | 700 |
| IT_TELEMETRY | 11,700 | 100 |
| OPERATIONS | 93,600 | 800 |
| INTEGRATION | 139,230 | 1,190 |
| **ИТОГО** | **635,310** | **5,430** |

## 2. Единовременные услуги (не проверены)

Строки смет без подтверждённых источников; заметная часть, вероятно, завышена (например, LEGAL 2.1 противоречит плану по валюте). Показаны отдельно и не входят в основной срок окупаемости.

| Блок | RSD | EUR |
|------|-----|-----|
| LEGAL | 3,276,000 | 28,000 |
| MARKETING | 234,000 | 2,000 |
| DOCUMENTATION | 1,053,000 | 9,000 |
| **ИТОГО** | **4,563,000** | **39,000** |

## 3. Постоянные расходы в месяц

| Строка | Описание | RSD/мес |
|--------|----------|---------|
| 3.3 | Maintenance and repair cost per site | 9,360 |
| 3.4 | Filter replacement cartridge | 975 |
| 5.1 | Site rental cost per month | 17,550 |
| 6.2 | GPS tracker subscription (data plan) | 1,170 |
| 6.6 | Remote monitoring platform subscription | 4,095 |
| 7.2 | Service interval and maintenance scheduling | 3,900 |
| | **ИТОГО** | **37,050** (~317 EUR) |

## 4. Переменные расходы и допущения

- Цена: 50 RSD за 5 л (10 RSD/л).
- Вода: тариф 158.09 RSD/м³, забор в 4 раза больше проданного объёма из-за сброса RO (допущение, уточнить у поставщика): 0.63 RSD/л.
- Комиссия платёжного провайдера: 1.5% выручки (нижняя граница 1,5–3%).
- Налог: 10% выручки.
- Вклад с литра после переменных затрат: 8.22 RSD.

## 5. Сценарии

| Сценарий | л/день | Выручка/мес | Переменные | Налог | Чистая прибыль/мес | Окупаемость оборудования (мес) | Окупаемость с услугами (мес) |
|----------|--------|-------------|-----------|-------|--------------------|-------------------------------|------------------------------|
| консервативный | 50 | 15,000 | 1,174 | 1,500 | -24,724 | не окупается | не окупается |
| реалистичный | 80 | 24,000 | 1,878 | 2,400 | -17,328 | не окупается | не окупается |

**Безубыточность по текущим расходам: ≈150 л/день.**

## 6. Исключённые строки смет

| Строка | Блок | Описание | RSD | Причина |
|--------|------|----------|-----|---------|
| 1.2 | TECH | Coin acceptor model selection | 14,040 | приём наличных вне пилота (решение 0001) |
| 1.3 | TECH | Bill acceptor model selection | 34,515 | приём наличных вне пилота (решение 0001) |
| 2.4 | LEGAL | Franchise legal framework for open zones | 2,925,000 | франшиза отложена (решения 0005, 0011) |
| 3.1 | FINANCE | Water cost per 5L unit (supplier contract) | 4,095 | переменная стоимость воды считается по тарифу (факт 0003); строка противоречит ему |
| 3.2 | FINANCE | Monthly site rent/electricity cost per site | 17,550 | дубль аренды 5.1 |
| 3.6 | FINANCE | Franchise fee (if applicable) per zone | 585,000 | франшиза отложена (решения 0005, 0011) |
| 4.1 | MARKETING | Single price model per 5L unit | 234 | цена пилота 50 RSD за 5 л (решение 0004); строка (2 EUR за 5 л) ей противоречит |
| 4.2 | MARKETING | Different price by location type (office vs kitchen) | 292 | дифференцированная цена отложена (решение 0004) |
| 4.3 | MARKETING | Subscription model for offices (volume cap) | 5,850 | офисные подписки отложены (решение 0003) |
| 4.4 | MARKETING | Franchise scaling to Balkan region | 2,340,000 | масштабирование на Балканы отложено (решения 0006, 0011) |
| 5.3 | LOCATIONS | Office location subscription model setup | 7,020 | офисы отложены (решение 0003) |
| 5.4 | LOCATIONS | Professional area (kitchen) machine configuration | 35,100 | кухни отложены (решение 0003) |
| 6.1 | IT_TELEMETRY | GPS tracker hardware module | 8,775 | дубль GPS 1.6 |
| 6.3 | IT_TELEMETRY | Camera system for remote monitoring | 23,400 | дубль камеры 1.5 |
| 6.4 | IT_TELEMETRY | Telemetry - water temperature sensor | 5,265 | дубль датчиков 1.7 |
| 7.3 | OPERATIONS | Anti-vandalism body protection | 40,950 | дубль антивандальной защиты 1.10 |
| 9.1 | GRANTS_AND_SUPPORT | Subsidija za samozapošljavanje (National Employment Service) | 380,000 | источник финансирования, а не расход |
| 9.2 | GRANTS_AND_SUPPORT | Vrati se i stvaraj (Ministry of Economy) | 1,800,000 | источник финансирования, а не расход |
| 9.3 | GRANTS_AND_SUPPORT | Kapital za razvoj (RAS) | 15,000,000 | источник финансирования, а не расход |
| 9.4 | GRANTS_AND_SUPPORT | StarTech (NALED + Philip Morris) | 15,000 | источник финансирования, а не расход |
| 9.5 | GRANTS_AND_SUPPORT | Smart Start (Innovation Fund) | 80,000 | источник финансирования, а не расход |
| 9.6 | GRANTS_AND_SUPPORT | Program for beginning entrepreneurs (Chamber of Commerce) | 30,000 | источник финансирования, а не расход |

## 7. Источники

- Затраты: docs/pipeline/estimates/*.md; курсы: fx.py (NBS).
- Допущения: решения 0001, 0003, 0004, 0011; факты 0003, 0005, 0007.