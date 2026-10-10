# Процесс обработки ответов и обновления документации

Этот документ описывает стандартную процедуру после получения ответов от поставщиков (RFQ) и органов (авторитеты).

---

## 1. При получении котировки от поставщика

### 1.1 Сохранение
1. Сохранить оригинал котировки (PDF/email) в `material/economics/correspondence/`:
   `SUPPLIERCODE_YYYY-MM-DD_quote.pdf`
2. Сохранить все приложения (документы CE, паспорта, спецификации) в соответствующие папки:
   - `material/economics/documents/` — нормативные документы
   - `material/economics/prices/` — коммерческие предложения
   - `material/economics/certificates/` — сертификаты соответствия

### 1.2 Обновление реестра источников
```bash
# Добавить запись в material/sources-registry.csv
track: economics
source_file: project/supplier-rfq.md
url: file://material/economics/correspondence/SUPPLIERCODE_YYYY-MM-DD_quote.pdf
category_guess: prices
local_path: economics/correspondence/SUPPLIERCODE_YYYY-MM-DD_quote.pdf
status: downloaded
notes: Official quote from [Supplier Name]
```

### 1.3 Заполнение таблицы сравнения
Открыть `material/economics/correspondence/rfq-tracking.md` и заполнить колонку поставщика в разделе 2.

### 1.4 Обновление сметных блоков
**TECH.md** строка 1.1 (RO base unit):
- `unit price`: подтверждённая цена (EUR/USD)
- `source`: `material/economics/correspondence/SUPPLIERCODE_YYYY-MM-DD_quote.pdf`

**LEGAL.md** — если есть новые данные по таможне/НДС от брокера.

**GRANTS_AND_SUPPORT.md** — обычно не меняется.

### 1.5 Пересчёт сценариев
```bash
python3 pipeline/calculator.py
```
Проверяет: `docs/cost-estimates/pilot-scenarios.md` обновился.

### 1.6 Обновление отчётов
- `docs/hardware/equipment-cost-estimate.md` — таблица позиций с новой ценой
- `docs/hardware/hardware-report.md` — раздел 3 (найденные цены), раздел 4 (неизвестные)
- `docs/economics/ready-made-options-landed-cost.md` — door-to-door расчёт
- `docs/economics/economics-report.md` — раздел 3 (точные цены), раздел 4 (неизвестные)
- `docs/project/pilot-launch-guide.md` — §2.3 таблица спецификации

### 1.7 Принятие решения
Заполнить решение владельца (0012 → active) с указанием выбранного варианта и обоснованием.

---

## 2. При получении ответа от органа

### 2.1 Сохранение
Сохранить входящий документ в `material/certification/correspondence/`:
`ORG_YYYY-MM-DD_incoming.pdf`

### 2.2 Обновление реестра источников
```bash
# Добавить/обновить запись в material/sources-registry.csv
track: certification
source_file: certification/certification-report.md
url: file://material/certification/correspondence/ORG_YYYY-MM-DD_incoming.pdf
category_guess: correspondence
local_path: certification/correspondence/ORG_YYYY-MM-DD_incoming.pdf
status: downloaded
notes: Official response from [Organ Name] re: [topic]
```

### 2.3 Обновление authority-tracking.md
Открыть `material/certification/correspondence/authority-tracking.md`:
- Заполнить дату ответа, вх. номер, файл ответа
- Заполнить «Ключевой результат» на основе ответа

### 2.4 Обновление карты требований
`docs/certification/requirements-map.md`:
- Найти строку органа/требования
- Заменить «[уточнить]» на подтверждённые данные
- В колонке «Источник» добавить: `material/certification/correspondence/ORG_YYYY-MM-DD_incoming.pdf`
- Обновить «Цена», «Срок», «Статус»

### 2.5 Обновление чек-листа допуска
`docs/certification/costs-and-timeline.md` §3:
- Отметить соответствующий пункт как ✅ (если требование выполнено/подтверждено)
- Добавить примечание с ссылкой на ответ

### 2.6 Закрытие неизвестных
`docs/reports/unknowns-and-open-issues.md`:
- Найти соответствующие ID (CE-XX, HW-XX, EC-XX, SM-XX)
- Изменить статус на «решено» с указанием документа-ответа
- Удалить из активного списка блокеров

### 2.7 Обновление отчётов дорожек
В зависимости от темы ответа:

| Орган / Тема | Обновляемые файлы |
|-------------|-------------------|
| 1. Минздрав / Санитарная инспекция | `certification-report.md` (вода), `sampling-report.md` (программа проб), `hardware-report.md` (материалы) |
| 2. Минсельхоз / Минздрав (пища) | `certification-report.md` (безопасность пищи) |
| 3. DMDM | `certification-report.md` (метрология), `hardware-report.md` (HW-04 дозатор) |
| 4. PURS | `certification-report.md` (фискализация), `economics-report.md` (фискал. модуль), `hardware-report.md` (терминал) |
| 5. RATEL | `certification-report.md` (радио), `hardware-report.md` (GPS/GSM модули) |
| 6. Минпром | `certification-report.md` (LVD/EMC, давление), `hardware-report.md` (техдок) |
| 7. ГЗЈЗ / Лаборатория | `sampling-report.md` (программа, цены, логистика), `certification-report.md` (вода) |
| 8. BVK | `certification-report.md` (монтаж), `pilot-launch-guide.md` §5-6, `economics-report.md` (тарифы) |
| 9. GO Surčin | `certification-report.md` (монтаж), `pilot-launch-guide.md` §5, `hardware-report.md` (площадки) |
| 10. Повереник | `certification-report.md` (вне сертификации), `hardware-report.md` (телеметрия/приватность) |
| 11. АПР / Бухгалтер | `certification-report.md` (деятельность), `economics-report.md` (НДС), `pilot-launch-guide.md` §3.2, §7.1 |

### 2.8 Пересчёт при изменении цен
Если ответы содержат цены (лаборатория, BVK, DMDM, ESIR, брокер):
```bash
python3 pipeline/calculator.py      # сценарии пилота
python3 pipeline/sampling_cost.py   # стоимость проб
python3 pipeline/economics.py       # финансовая модель
python3 pipeline/inventory.py       # модель запаса
```
Проверить: `docs/cost-estimates/pilot-scenarios.md`, `docs/sampling/program-costs.md`, `docs/economics/pricing-scenarios.md`, `docs/economics/inventory-model.md`.

---

## 3. Еженедельный аудит (понедельник)

1. Проверить `authority-tracking.md` и `rfq-tracking.md` — какие ответы получены, какие ожидаются.
2. Проверить `docs/reports/unknowns-and-open-issues.md` — какие блокеры остались открыты.
3. Запустить верификацию: `python3 pipeline/verify.py` — должно быть "All estimate checks passed".
4. Обновить `docs/reports/final-report.md` §6 («Что блокирует главные решения») — убрать закрытые, добавить новые.
5. Краткий статус-репорт владельцу: что получено, что ожидается, какие решения нужны.

---

## 4. Контроль версий

Все изменения в документации фиксируются коммитами с префиксами:
- `docs(hardware): update equipment costs from [Supplier] quote`
- `docs(certification): update requirements map from [Organ] response`
- `docs(economics): recalc pilot scenarios after [source] prices`
- `docs(sampling): update program costs from [Lab] price list`
- `chore(material): archive [source] to material/...`

---

## 5. Чек-лист готовности к запуску (перед шагом 12 pilot-launch-guide.md)

- [ ] Все 14 пунктов чек-листа допуска (`costs-and-timeline.md` §3) — ✅ с локальными ссылками
- [ ] `final-report.md` §6 — нет критических блокеров («не найдено» только по неблокирующим позициям)
- [ ] `pilot-scenarios.md` — пересчитан с последними ценами
- [ ] Договор с поставщиком подписан, аванс оплачен
- [ ] Юрлицо зарегистрировано, счёт открыт
- [ ] Площадка выбрана, договор аренды подписан
- [ ] BVK ТУ получены, подключение согласовано
- [ ] Лаборатория выбрана, договор подписан, пробоотборник обучен
- [ ] Фискальный модуль выбран, интеграция протестирована
- [ ] Страхование оформлено (если решение владельца)
- [ ] Листок допуска подписан двумя лицами

---

*Документ версии 1.0. Обновляется по мере уточнения процессов.*