# Запрос котировок (RFQ) на аппарат для пилота

> Обновлен 2026-10-11 по решению владельца `strebulaev`: одна наружная точка у многоквартирного жилого дома в Сурчине, доступ 24/7, оплата наличными и безналично. Ничего не отправлено. Текст запроса — на английском, пояснения для команды — на русском.
> Для решения `0012`: запросить письменные предложения у 2–3 китайских производителей (вариант A), одного европейского (D) и одного местного дистрибьютора (B), затем сравнить по таблице в конце. Отправка запросов требует отдельной команды владельца и пока не разрешена.
> Перед будущей отправкой подставить `[…]` (название DOO, контакт, точный адрес/город установки, целевой срок).

## Кому отправлять

| Вариант | Кого искать | Где |
|---|---|---|
| A | 2–3 производителя RO-вендинга с историей экспорта в ЕС/Балканы (уточнять модель RO-300A / RO-300J / KN-RO-300A) | Alibaba/Made-in-China (платёжная защита платформы), прямые сайты производителей |
| D | Европейский производитель (например, Ecosoft: страница Aquabox RO vending, на ней указана цена 6 541,67 EUR без НДС — подтвердить котировкой) | https://ecosoft.com/product-ecosoft/vend-ka250robcdm-v3 |
| B | Белградский импортёр/дистрибьютор вендинга воды; по публикации 2022 года аппарат в Зренянине принадлежал компании «Vodomati Vessa» (Белград), импортёру аппаратов «Živa Voda» (Россия); контакты не найдены, искать самим | прямой запрос; узнать, продают ли аппараты третьим лицам; актуальность компании в 2026 не проверена |

Важно для B: та же фирма — потенциальный конкурент. Не раскрывать лишних планов (цены, площадки); спрашивать только про аппарат, документы и сервис.

## Текст запроса (английский)

**Subject:** RFQ – 1 outdoor self-service drinking water vending machine (RO), cash and cashless, delivery to Serbia

Hello,

We are a Serbian d.o.o. preparing a pilot of one outdoor self-service drinking water vending point by a residential apartment building in Surčin. Customers should have access 24/7. Please quote **1 unit** (with the option of further units after the pilot). The exact site address and machine supplier have not yet been selected.

**1. Machine**
- Reverse-osmosis purified water from the municipal supply (cold water, drain line available); please state the exact model name, rated capacity, the minimum and maximum inlet pressure, the number of filtration stages and the storage tank volume.
- Dispensing: 5 L and 19 L (5 gal) bottles; please state the dispensing flow (L/min); stainless-steel removable nozzle, drip tray, leak protection.
- Mains: European 230 V / 50 Hz; please state the supply voltage range, power draw and plug type.
- Cabinet: steel with polycarbonate panels, key lock, floor anchoring, anti-vandal design for unattended use; please state steel thickness, dimensions and weight.
- Outdoor-rated enclosure and removable or switchable heater for freeze protection (thermostat, summer-mode disable); please state the supported outdoor temperature/moisture range, ingress protection rating and test basis, heater power and thermostat setpoint. Do not assume an unverified protection rating.

**2. Payment and control**
- Both cash and cashless payment are required for this pilot. For cashless, quote contactless card/phone (EMV NFC) and state available QR options. For cash, quote compatible coin and banknote acceptance modules that can return change; list supported denominations, escrow/refund behavior, cassette details, configurations and prices separately. Change payout is a buyer requirement.
- Controller must expose MDB or another documented interface so that the payment/fiscal system can be integrated. Please send protocol/API documentation and transaction-state diagrams for approval-before-dispense, payment failure, cancellation and refund.
- State whether you can integrate a fiscal solution accepted for Serbian vending sales for both payment types. Identify the provider, certificate reference and exact supported machine/module models. A payment reader alone is not a fiscal solution.
- Describe cash reconciliation logs, cassette capacity/removal procedure, tamper alarm and whether safe service requires your staff or a local operator.

**3. Telemetry**
- Remote monitoring of: sales events, water temperature, flow, door opening, fault alarms, GPS position. 2 MP IP camera. Cellular (GSM/LTE) modem with a documented data format and API, no mandatory vendor cloud lock-in; please state any subscription fees.
- Fail-safe: dispensing blocked when the selected payment method is unavailable or not confirmed; watchdog restart. Cash and cashless transaction events must be separately exportable for reconciliation.

**4. Compliance and documents** (please attach with the quotation)
- Declaration of conformity (CE, LVD, EMC) and test reports.
- Certificates/declarations that all wetted parts (tank, tubing, fittings, membranes, nozzle) are food-grade for drinking water, with the applicable standard (EU 10/2011, NSF/ANSI 61 or equivalent).
- Filter/membrane specification, expected life and replacement cost per set; water quality test report of a comparable unit.
- HS code and country of origin.

**5. Commercial terms**
- Separate itemized unit prices for base machine, cashless terminal, coin acceptor/changer, banknote acceptor, fiscal integration, outdoor protection/heater, and optional parts; quote **EXW/FOB [port] and DAP [full delivery address after selection]**, in EUR or USD; validity of offer. CIF port price alone is not a door-to-door price.
- Lead time, packaging dimensions and weight, minimum order quantity.
- Payment terms (we propose staged payment: deposit and balance against shipping documents, preferably via the platform's payment protection).
- Warranty (at least 12 months), spare-parts and consumables list with prices, availability of remote technical support, language of the user interface (Serbian or English).
- Acceptance: factory acceptance test with video before shipment; **signed tolerance sheet** (critical dimensions and fits) with a penalty for deviations; replacement of non-conforming parts at the supplier's cost.
- Reference installations in Europe/the Balkans, if any.

Please reply by **[date]**. Thank you.

[Name, company, phone, email]

## Дополнительные вопросы только местному дистрибьютору (B)

- Какие санитарные документы и разрешения уже есть на аппарат в Сербии и на чьё имя (импортёр, производитель)?
- Цена «под ключ»: аппарат, доставка, установка, подключение, запуск; условия аренды вместо покупки.
- Сервис: график, время реакции, запасные части в Сербии, стоимость визита.
- Помощь с анализом воды в институте и с фискализацией; есть ли готовое сертифицированное решение для оплаты.
- Можно ли посмотреть работающие площадки и результаты анализов воды.

## Таблица сравнения котировок

| Критерий | A1 | A2 | A3 | D | B |
|---|---|---|---|---|---|
| Цена аппарата, EUR (FOB/CIF) | | | | | |
| Фрахт, пошлина, НДС, брокер (оценка) | | | | | |
| Итого с доставкой и формальностями, EUR | | | | | |
| Подтверждено ступеней / бак / наружная защита / напряжение | | | | | |
| Cash: coin + note module, denominations, change/refund, cassette service | | | | | |
| Cashless: EMV/NFC, supported Serbian acquirer, fee | | | | | |
| Serbian fiscal integration accepted for vending (both modes) | | | | | |
| Cash handling/safety/reconciliation service costs | | | | | |
| Документы на материалы контакта с водой | | | | | |
| CE / LVD / EMC | | | | | |
| Протокол/API оплаты и телеметрии | | | | | |
| Гарантия, запчасти, удалённая поддержка | | | | | |
| Срок изготовления | | | | | |
| Условия оплаты и допуски со штрафами | | | | | |
| Референс-площадки | | | | | |

Правило выбора между вариантами (порог отношения цен) — предложение, решение `0012`: порог не определён, ждёт котировок и решения владельца. Для справки: опубликованная цена Ecosoft 6 541,67 EUR без НДС (страница открыта); цена варианта A — не найдена (нужны котировки). После получения котировок записать подтверждённые цифры в сметы (решение 0009) и обновить `pilot-launch-guide.md` §2.3.
