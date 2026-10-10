# Сценарии пилотной точки

Сгенерировано `pipeline/calculator.py` для одного жилого аппарата, только безналичная оплата (решения 0001, 0003, 0005, 0011). Скрипт не подставляет догадки: ячейки сметы со значением `not found` пропускаются и перечисляются ниже; суммы показаны только как «по найденным позициям». Курсы: 1 EUR = 117,4601 RSD, 1 USD = 104,7068 RSD (`pipeline/fx.py`, НБС на 6.10.2026 через biznis.kurir.rs, вторичный источник); RSD округлены до динара, EUR до евро. Реестр неизвестного: `docs/reports/unknowns-and-open-issues.md`.

## 1. Единовременные затраты на оборудование и установку

**По найденным позициям: 1 из 27 позиций.** Итог по всем позициям не определён.

| Блок | RSD (найденные позиции) | EUR |
|------|-----|-----|
| TECH | 40,836 | 348 |
| **По найденным позициям** | **40,836** | **348** |

Позиции без найденной цены (в сумму не входят):

- TECH: 1.1 Water vending machine - RO base unit only (cashless reader, GPS, camera, sensors and heater are items 1.4-1.8); 1.5 Camera module for monitoring (working/trashed/stolen scenarios); 1.6 GPS tracker module; 1.7 Telemetry system (water temperature, freezing risk); 1.8 Heater (removable/switchable, summer removal to prevent theft); 1.9 Machine assembly coordination (contractor vs in-house); 1.10 Anti-vandalism protection (body and unit shielding)
- LOCATIONS: 5.2 Electricity consumption tracking installation; 5.5 Residential building placement negotiation
- IT_TELEMETRY: 6.5 Payment integration (cashless API with Serbian providers)
- OPERATIONS: 7.1 Machine repairability - spare parts warehouse setup
- INTEGRATION: 10.1 Camera mount and cable; 10.2 GPS mount and cable; 10.3 Temperature sensors mount and cable; 10.4 Flow sensor mount and cable; 10.5 Door sensor mount and cable; 10.6 GSM antenna mount and cable; 10.7 Wiring controller to payment module; 10.8 Wiring controller to telemetry; 10.9 Heater wiring and switch; 10.10 Controller firmware and configuration; 10.11 Telemetry account and platform setup; 10.12 Bench integration test; 10.13 On-site integration test; 10.14 Integration labour; 10.15 Integration documentation (diagram, config)

## 2. Единовременные услуги

**По найденным позициям: 1 из 8 позиций.**

| Блок | RSD (найденные позиции) | EUR |
|------|-----|-----|
| LEGAL | 8,000 | 68 |
| **По найденным позициям** | **8,000** | **68** |

Позиции без найденной цены (в сумму не входят):

- LEGAL: 2.2 Tax regime assessment (bottled water 20%, rest 10%); 2.3 Cash vs cashless declaration requirements
- MARKETING: 4.5 Marketing Ps (Product, Price, Place, Promotion) analysis
- DOCUMENTATION: 8.1 Detailed cost estimate document preparation; 8.2 Business plan development; 8.3 Financial plan development; 8.4 Project documentation (engineering pack)

## 3. Постоянные расходы в месяц

**По найденным позициям: 0 из 6 позиций.** Сумма постоянных расходов F не определена.

Ни одна постоянная статья не имеет найденной цены (сумма по найденным позициям: 0 из 6).

Позиции без найденной цены (аренда, обслуживание, платформа мониторинга, SIM, фильтры):

- FINANCE: 3.3 Maintenance and repair cost per site; 3.4 Filter replacement cartridge
- LOCATIONS: 5.1 Site rental cost per month
- IT_TELEMETRY: 6.2 GPS tracker subscription (data plan); 6.6 Remote monitoring platform subscription
- OPERATIONS: 7.2 Service interval and maintenance scheduling

## 4. Известные входные данные и формулы

- Цена (решение владельца, 0004): 50 RSD за 5 л, то есть p = 10 RSD/л (включает ли цена НДС — не определено).
- Тариф BVK 2026, прочие потребители, с НДС (факт 0003, вторичный источник): вода 158.09 RSD/м³, водоотведение 85.07 RSD/м³; порядок начисления на сброс RO не найден.
- Вода на 1 л проданной воды: w = k × 158.09/1000 RSD (только вода) или k × (158.09 + 85.07)/1000 RSD (с водоотведением), где k — не найдено.
- Вклад с литра: c = p × (1 − f − t) − w. Выручка в месяц при V л/день: R = p × V × 30 (по цене покупателя).
- Прибыль в месяц: P(V) = c × V × 30 − F. Безубыточность: V* = F / (30 × c).

Не найдены входные данные, без которых c, F, P и V* не определены:

- k - литров воды из сети на литр проданной (сброс RO): не найдено, спросить поставщика аппарата
- f - комиссия эквайрера, доля выручки: не найдено, спросить банки-эквайреры
- t - налог на выручку / режим НДС для воды из аппарата: не найдено, спросить бухгалтера и Налоговую администрацию
- F - постоянные расходы: найдена часть позиций, см. раздел 3 (аренда, обслуживание, платформа, SIM, фильтры: не найдено).

## 5. Сценарии объёма

Объём в литрах в день — свободная переменная решения, не прогноз. Вычислима только выручка по цене покупателя; прибыль, налоги и окупаемость **не определены** (нужны k, f, t, F).

| Сценарий | л/день | Выручка/мес по цене покупателя, RSD | Чистая прибыль/мес | Окупаемость |
|----------|--------|-----------------------------------|--------------------|-------------|
| низкий объём | 50 | 15,000 | не определено | не определено |
| более высокий объём | 80 | 24,000 | не определено | не определено |

Безубыточность: **не определена** (формула V* в разделе 4). Критерий пилота 50 л/день — минимум спроса, а не безубыточность (решение 0011).

## 6. Исключённые строки смет

| Строка | Блок | Описание | RSD | Причина |
|--------|------|----------|-----|---------|
| 1.2 | TECH | Coin acceptor model selection | не найдено | приём наличных вне пилота (решение 0001) |
| 1.3 | TECH | Bill acceptor model selection | не найдено | приём наличных вне пилота (решение 0001) |
| 2.4 | LEGAL | Franchise legal framework for open zones | не найдено | франшиза отложена (решения 0005, 0011) |
| 3.1 | FINANCE | Water cost per 5L unit (supplier contract) | не найдено | переменная стоимость воды считается отдельно по тарифу (факт 0003); строка исключена, чтобы не считать дважды |
| 3.2 | FINANCE | Monthly site rent/electricity cost per site | не найдено | дубль аренды 5.1 |
| 3.5 | FINANCE | Cashless payment transaction fee | не найдено | комиссия считается от выручки |
| 3.6 | FINANCE | Franchise fee (if applicable) per zone | не найдено | франшиза отложена (решения 0005, 0011) |
| 4.1 | MARKETING | Single price model per 5L unit | 50 | цена пилота 50 RSD за 5 л (решение 0004); строка (2 EUR за 5 л) ей противоречит |
| 4.2 | MARKETING | Different price by location type (office vs kitchen) | не найдено | дифференцированная цена отложена (решение 0004) |
| 4.3 | MARKETING | Subscription model for offices (volume cap) | не найдено | офисные подписки отложены (решение 0003) |
| 4.4 | MARKETING | Franchise scaling to Balkan region | не найдено | масштабирование на Балканы отложено (решения 0006, 0011) |
| 5.3 | LOCATIONS | Office location subscription model setup | не найдено | офисы отложены (решение 0003) |
| 5.4 | LOCATIONS | Professional area (kitchen) machine configuration | не найдено | кухни отложены (решение 0003) |
| 6.1 | IT_TELEMETRY | GPS tracker hardware module | не найдено | дубль GPS 1.6 |
| 6.3 | IT_TELEMETRY | Camera system for remote monitoring | не найдено | дубль камеры 1.5 |
| 6.4 | IT_TELEMETRY | Telemetry - water temperature sensor | не найдено | дубль датчиков 1.7 |
| 7.3 | OPERATIONS | Anti-vandalism body protection | не найдено | дубль антивандальной защиты 1.10 |
| 9.1 | GRANTS_AND_SUPPORT | Subsidija za samozapošljavanje (National Employment Service) | 380,000 | источник финансирования, а не расход |
| 9.2 | GRANTS_AND_SUPPORT | Vrati se i stvaraj (Ministry of Economy) | 1,800,000 | источник финансирования, а не расход |
| 9.3 | GRANTS_AND_SUPPORT | Kapital za razvoj (Ministry of Economy, RAS) | 15,000,000 | источник финансирования, а не расход |
| 9.4 | GRANTS_AND_SUPPORT | StarTech (NALED) | 5,235,340 | источник финансирования, а не расход |
| 9.5 | GRANTS_AND_SUPPORT | Pametni pocetak / Smart Start (Innovation Fund) | 5,400,000 | источник финансирования, а не расход |
| 9.6 | GRANTS_AND_SUPPORT | Program podrske pocetnicima u poslovanju (programme for business starters) | 3,600,000 | источник финансирования, а не расход |

## 7. Источники

- Затраты: `docs/cost-estimates/blocks/*.md` (только строки с URL/путём как источником); курсы: `pipeline/fx.py`.
- Входные данные: решение 0004 (цена, решение владельца); факт 0003 (тарифы BVK, вторичный источник).
- Строки блока GRANTS_AND_SUPPORT выражены в RSD (BLOCK_CURRENCY); остальные блоки — в EUR.
