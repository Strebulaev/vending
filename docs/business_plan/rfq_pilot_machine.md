# Запрос котировок (RFQ) на аппарат для пилота

> Черновик от 2026-10-08. Ничего не отправлено. Текст запроса — на английском, потому что уходит поставщикам; пояснения для команды — на русском.
> Для решения `0012`: разослать **один и тот же** запрос 2–3 китайским производителям (вариант A), одному европейскому (D) и одному местному дистрибьютору (B), затем сравнить по таблице в конце.
> Перед отправкой подставить `[…]` (название компании, контакт, город установки).

## Кому отправлять

| Вариант | Кого искать | Где |
|---|---|---|
| A | 2–3 производителя RO-вендинга с историей экспорта в ЕС/Балканы (уточнять модель RO-300A / RO-300J / KN-RO-300A) | Alibaba/Made-in-China (платёжная защита платформы), прямые сайты производителей |
| D | Европейский производитель (например, Ecosoft: страница Aquabox RO vending) | сайт производителя |
| B | Белградский импортёр/дистрибьютор вендинга воды; оператор, ввозящий аппараты российского производства | прямой запрос; узнать, продают ли аппараты третьим лицам |

Важно для B: та же фирма — потенциальный конкурент. Не раскрывать лишних планов (цены, площадки); спрашивать только про аппарат, документы и сервис.

## Текст запроса (английский)

**Subject:** RFQ – 1 pcs self-service drinking water vending machine (RO), delivery to Serbia

Hello,

We are a Serbian start-up preparing a pilot of one self-service drinking water vending point and request a firm quotation for **1 unit** (with the option of further units after the pilot).

**1. Machine**
- Reverse-osmosis purified water from the municipal supply (cold water, inlet pressure at least 0.2 MPa, drain line available); capacity about 400 GPD; please state the exact model name and confirm the number of filtration stages and the storage tank volume.
- Dispensing: 5 L and 19 L (5 gal) bottles, dispensing flow about 8 L/min, stainless-steel removable nozzle, drip tray, leak protection.
- Mains: 220–230 V / 50 Hz; please state power draw and plug type.
- Cabinet: steel (about 2 mm) with polycarbonate panels, key lock, floor anchoring (M12), anti-vandal design for unattended indoor use; please state dimensions and weight.
- Removable or switchable heater for freeze protection (thermostat at about +2 °C, summer-mode disable).

**2. Payment and control**
- Cashless only for this order: contactless card/phone (EMV NFC) and, if possible, QR payment. Coin/bill acceptors are not required.
- Controller with MDB or documented open protocol so that a Serbian fiscal/payment module can be integrated. Please send the protocol/API documentation.
- Please state whether the payment reader supports certified fiscal integration in your reference markets.

**3. Telemetry**
- Remote monitoring of: sales events, water temperature, flow, door opening, fault alarms, GPS position. 2 MP IP camera. Cellular (GSM/LTE) modem with a documented data format and API, no mandatory vendor cloud lock-in; please state any subscription fees.
- Fail-safe: dispensing blocked when payment is unavailable; watchdog restart.

**4. Compliance and documents** (please attach with the quotation)
- Declaration of conformity (CE, LVD, EMC) and test reports.
- Certificates/declarations that all wetted parts (tank, tubing, fittings, membranes, nozzle) are food-grade for drinking water, with the applicable standard (EU 10/2011, NSF/ANSI 61 or equivalent).
- Filter/membrane specification, expected life and replacement cost per set; water quality test report of a comparable unit.
- HS code and country of origin.

**5. Commercial terms**
- Unit price and prices of optional items, quoted **EXW/FOB [port] and CIF [Belgrade or Thessaloniki]**, in EUR or USD; validity of the offer.
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
| Подтверждено ступеней / бак / напряжение | | | | | |
| Документы на материалы контакта с водой | | | | | |
| CE / LVD / EMC | | | | | |
| Протокол/API оплаты и телеметрии | | | | | |
| Гарантия, запчасти, удалённая поддержка | | | | | |
| Срок изготовления | | | | | |
| Условия оплаты и допуски со штрафами | | | | | |
| Референс-площадки | | | | | |

Правило решения `0012`: выбрать B или D, если их итоговая цена не выше ~2× от лучшей котировки A; иначе A с допусками и штрафами по договору. После получения котировок записать подтверждённые цифры в сметы (решение 0009) и обновить `pilot_implementation.md` §2.3.
