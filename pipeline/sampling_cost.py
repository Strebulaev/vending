"""Параметрическая модель стоимости программы отбора проб воды.

Запуск из корня репозитория:  python3 pipeline/sampling_cost.py
Результат: docs/sampling/costs.md

ВАЖНО: цены лабораторных анализов НЕ НАЙДЕНЫ в открытых источниках. Все цены
анализов ниже - допущения (три сценария), которые нужно заменить прайсом
лаборатории (вопросы - docs/sampling/REPORT.md). Модель не содержит рыночных котировок.
Курсы: fx.py (1 EUR = 117 RSD, 1 USD = 107 RSD).
"""

import math
import os

from fx import EUR_TO_RSD, USD_TO_RSD

SCEN = ("low", "mid", "high")
SCEN_RU = {"low": "низкий", "mid": "средний", "high": "высокий"}

# ---------------------------------------------------------------- цены, RSD
# Лабораторные пакеты анализов: [допущение], заменить прайсом лаборатории.
LAB = {
    # микро-пакет: E. coli, колиформы, энтерококки, P. aeruginosa, число аэробных мезофильных 37 C
    "micro": {"low": 2500, "mid": 5000, "high": 9000},
    # короткая физико-химия: pH, электропроводность, мутность, цвет, запах/вкус, KMnO4, NH3, NO2, NO3, Cl-
    "phys_short": {"low": 4000, "mid": 9000, "high": 16000},
    # расширенные металлы/неорганика: As, Pb, Cu, Ni, Cd, Hg, Cr, Na, F, B, Sb, Se, Zn, Fe, Mn, Al, сульфаты
    "metals_ext": {"low": 8000, "mid": 20000, "high": 40000},
    # выезд пробоотборника лаборатории за один визит (альтернатива самостоятельному отбору)
    "lab_visit": {"low": 3000, "mid": 6000, "high": 12000},
}

# Расходные материалы на пробу, RSD.
# Стерильная бутыль 250 мл с тиосульфатом: Buddeberg, 143,20 EUR без НДС за 108 шт. [web]
# https://shop.buddeberg.de/sample-preparation/sampling/sample-transport-storage/water-sample-bottles-pp/info895178_lang_uk.htm
BOTTLE_STERILE = {
    "low": 143.20 * EUR_TO_RSD / 108,
    "mid": 170.41 * EUR_TO_RSD / 108,      # с НДС 19% (Германия) [web]
    "high": 250.0,                          # [допущение] местная закупка малыми партиями + доставка
}
# Бутыль 1,5 л для химии (чистая бутыль из-под негазированной воды по инструкции ГЗЈЗ) и мелочь
# (лёд-аккумуляторы, перчатки, спирт, тампон, этикетки): [допущение]
CONSUMABLE_OTHER = {"low": 100.0, "mid": 200.0, "high": 350.0}

# Транспорт и время пробоотборника. Расстояние Сурчин - лаборатория ~20 км в одну сторону [допущение]
TRIP_KM_ROUNDTRIP = 40
KM_COST = {"low": 15.0, "mid": 25.0, "high": 60.0}         # RSD/км (бензин / такси), [допущение]
TRIP_HOURS = 2.0                                            # отбор + дорога, [допущение]
HOUR_COST = {"low": 0.0, "mid": 800.0, "high": 1500.0}     # время основателя = 0 в низком сценарии, [допущение]
POINTS_PER_TRIP = 4                                         # точек за один рейс (лимит времени доставки), [допущение]

# ---------------------------------------------------------------- режим программы
CLUSTER_MAX = 10          # макс. число аппаратов в кластере (источник воды + конфигурация), [допущение]
ZONES = {1: 1, 5: 1, 20: 2, 50: 3}   # число зон водоснабжения BVK, [допущение]
ROUTINE_INTERVAL_MONTHS = {1: 1, 5: 2, 20: 2, 50: 2}   # микробиология на точку: 1 раз в N мес
CHEM_SHORT_INTERVAL_MONTHS = 3      # короткая химия на кластер
FULL_PER_CLUSTER_PER_YEAR = 1       # периодический полный анализ на кластер
UNPLANNED_PER_POINT_PER_YEAR = 1.0  # внеплановых событий на точку, [допущение]
MICRO_PER_ROUTINE_VISIT = 2         # вода на насадке + смыв/мазок насадки
UNPLANNED_MICRO = 5                 # 3 пробы + 2 повторные после санобработки
UNPLANNED_PHYS = 1

# Наборы пуска (число анализов) - docs/sampling/program.md
LAUNCH_LEAD = {"micro": 8, "phys_short": 4, "metals_ext": 2, "visits": 3}
LAUNCH_FOLLOW = {"micro": 7, "phys_short": 1, "metals_ext": 0, "visits": 3}

# Оборудование (разовое), RSD. Источники - в costs.md
EQUIPMENT = [
    ("Тестер TDS/EC карманный (Hanna HI98301, 73,79 USD)", 73.79 * USD_TO_RSD, "[web] https://www.hydrotekhydroponics.com/hanna-hi98301-ppm-tester-dist-1"),
    ("Комбо pH/EC метр (Hanna HI98129, 129-159 EUR, среднее)", 144.0 * EUR_TO_RSD, "[web] https://www.ebay.de/p/640300268 (объявления eBay.de)"),
    ("Набор DPD свободный хлор, вход (Hach 2438800, 62,15 USD)", 62.15 * USD_TO_RSD, "[web] https://supply.coreandmain.com/Hach-Chlorine-Free-and-Total-Reagent-Set-DPD-5-mL-2438800"),
    ("Термосумка/контейнер 20 л (Curver, 15,99 EUR)", 15.99 * EUR_TO_RSD, "[web] https://aio.lv/en/product--curver-159567--1028868"),
    ("Цифровой термометр (14-20 EUR, среднее 17)", 17.0 * EUR_TO_RSD, "[web] https://lioninox.com/en/products/basic-digital-thermometer"),
    ("Калибровочные растворы pH/EC на год", 3000.0, "[допущение]"),
]
EQUIPMENT_NOTE_EXTRA = (
    "Экспресс-тесты колиформ/E. coli (presence/absence, например Colitag 100 шт. = 431 USD "
    "https://www.cpiinternational.com/shop/4600-0013-colitag-test-kit-p-a-100ml-format-100-pk-7067 [web]) "
    "= ~461 RSD/тест, не заменяют лабораторию (WHO допускает полевые наборы при подтверждённой валидации); "
    "в базовую модель не включены."
)

FIXED_MONTHLY_SITE_RSD = 37050.0   # [repo] docs/pipeline/consolidated/pilot_scenarios.md §3


def clusters(n):
    return max(ZONES[n], math.ceil(n / CLUSTER_MAX))


def per_sample_consumables(s, kind):
    if kind == "micro":
        return BOTTLE_STERILE[s] + CONSUMABLE_OTHER[s] * 0.5
    return CONSUMABLE_OTHER[s]  # 1,5 л бутыль + мелочь


def trip_cost(s):
    return TRIP_KM_ROUNDTRIP * KM_COST[s] + TRIP_HOURS * HOUR_COST[s]


def analysis_cost(s, micro, phys, metals, price_mult=1.0):
    lab = (micro * LAB["micro"][s] + phys * LAB["phys_short"][s] + metals * LAB["metals_ext"][s]) * price_mult
    cons = micro * per_sample_consumables(s, "micro") + (phys + metals) * per_sample_consumables(s, "chem")
    return lab, cons


def monthly_events(n, interval=None, chem_interval=None, unplanned=None, full=None):
    """Число событий в месяц в установившемся режиме."""
    interval = interval or ROUTINE_INTERVAL_MONTHS[n]
    chem_interval = chem_interval or CHEM_SHORT_INTERVAL_MONTHS
    unplanned = UNPLANNED_PER_POINT_PER_YEAR if unplanned is None else unplanned
    full = FULL_PER_CLUSTER_PER_YEAR if full is None else full
    k = clusters(n)
    routine_visits = n / interval
    micro = routine_visits * MICRO_PER_ROUTINE_VISIT
    phys = k / chem_interval
    metals = k * full / 12
    micro += k * full / 12            # микро в составе полного анализа
    phys += k * full / 12
    unpl = n * unplanned / 12
    micro += unpl * UNPLANNED_MICRO
    phys += unpl * UNPLANNED_PHYS
    # рейсы: плановые визиты группируются; полный анализ и химия едут с плановым рейсом
    trips = max(1, math.ceil(routine_visits / POINTS_PER_TRIP))
    trips += unpl * 2                  # внеплановое: первая проба и повторная
    lab_visits = routine_visits + unpl * 2
    return {"micro": micro, "phys": phys, "metals": metals, "trips": trips, "lab_visits": lab_visits}


def monthly_cost(n, s, price_mult=1.0, lab_sampling=False, **kw):
    ev = monthly_events(n, **kw)
    lab, cons = analysis_cost(s, ev["micro"], ev["phys"], ev["metals"], price_mult)
    if lab_sampling:
        transport = ev["lab_visits"] * LAB["lab_visit"][s]
    else:
        transport = ev["trips"] * trip_cost(s)
    return {"lab": lab, "cons": cons, "transport": transport, "total": lab + cons + transport, **ev}


def launch_cost(n, s, price_mult=1.0):
    k = clusters(n)
    lead, follow = LAUNCH_LEAD, LAUNCH_FOLLOW
    micro = k * lead["micro"] + (n - k) * follow["micro"]
    phys = k * lead["phys_short"] + (n - k) * follow["phys_short"]
    metals = k * lead["metals_ext"] + (n - k) * follow["metals_ext"]
    visits = k * lead["visits"] + (n - k) * follow["visits"]
    lab, cons = analysis_cost(s, micro, phys, metals, price_mult)
    trips = visits  # на запуске один рейс = один визит
    transport = trips * trip_cost(s)
    return {"lab": lab, "cons": cons, "transport": transport, "total": lab + cons + transport,
            "micro": micro, "phys": phys, "metals": metals, "visits": visits}


def equipment_total():
    return sum(x[1] for x in EQUIPMENT)


def rsd(x):
    return f"{x:,.0f}".replace(",", " ")


def reorder_table(n, lead_days=8, safety_days=7, batch=60):
    """Расход стерильных бутылей и точка заказа (поставка lead_days дней)."""
    ev = monthly_events(n)
    daily = ev["micro"] / 30.0
    rop = daily * lead_days + daily * safety_days
    return daily, rop


def weekly_use(n=20, per_week=2):
    """Бутылей в неделю при запуске per_week точек в неделю: запуск + рутина запущенных ранее (раз в 4 нед.)."""
    rows, launched = [], 0
    for week in range(1, 15):
        new = min(per_week, n - launched)
        routine_points = max(0, launched - per_week * 2)   # рутина после 2 недель от запуска, упрощение
        launched += new
        rows.append((week, new, launched, new * LAUNCH_FOLLOW["micro"] + routine_points / 4.0 * MICRO_PER_ROUTINE_VISIT))
    return rows


def simulate_orders(stock0, q1, q=60, lead=8, safety=7, n=20, per_week=2):
    """Посуточная модель: заказ 1 в день 0 (приход в день lead), далее заказ по позиции запаса (на руках + в пути) <= ROP."""
    rows = weekly_use(n, per_week)
    peak = max(r[3] for r in rows) / 7.0
    rop = math.ceil(peak * (lead + safety))
    stock, orders, events, min_stock = stock0, [(0, lead, q1)], [f"день 0: заказ 1 на {q1} шт., приход день {lead}"], stock0
    for day in range(1, 99):
        week = min((day - 1) // 7, len(rows) - 1)
        stock -= rows[week][3] / 7.0
        for o in list(orders):
            if o[1] == day:
                stock += o[2]
                events.append(f"день {day}: приход партии {o[2]} шт., остаток {stock:.0f}")
                orders.remove(o)
        position = stock + sum(o[2] for o in orders)
        if position <= rop:
            orders.append((day, day + lead, q))
            events.append(f"день {day}: заказ на {q} шт. (позиция {position:.0f} <= ROP {rop}), приход день {day + lead}")
        min_stock = min(min_stock, stock)
        if stock < 0 and not any("нехватка" in e for e in events):
            events.append(f"день {day}: НЕХВАТКА тары (остаток {stock:.0f})")
    return rop, round(min_stock, 1), events[:14]


def main():
    global CLUSTER_MAX
    out = []
    w = out.append
    w("# Стоимость программы отбора проб (сгенерировано `pipeline/sampling_cost.py`)\n")
    w("> Не править вручную: файл перезаписывается скриптом. Курсы: 1 EUR = 117 RSD, 1 USD = 107 RSD [repo: pipeline/fx.py].\n")
    w("> **Цены лабораторных анализов не найдены** (ГЗЈЗ Белград, Батут, частные лаборатории не публикуют прайс; проверено поиском 2026-10-08). "
      "Сценарии ниже - **допущение**, а не котировки; заменить прайсом лаборатории (`REPORT.md`, список вопросов).\n")

    w("## 1. Допущения о ценах (RSD за единицу)\n")
    w("| Позиция | Низкий | Средний | Высокий | Источник |")
    w("|---|---:|---:|---:|---|")
    names = {"micro": "Микро-пакет (E. coli, колиформы, энтерококки, P. aeruginosa, аэробные мезофилы)",
             "phys_short": "Короткая физико-химия (pH, EC, мутность, цвет, запах/вкус, KMnO4, NH3, NO2, NO3, Cl)",
             "metals_ext": "Расширенные металлы/неорганика (As, Pb, Cu, Ni, Cd, Hg, Cr, Na, F, B, Sb, Se, Zn, Fe, Mn, Al, SO4)",
             "lab_visit": "Выезд пробоотборника лаборатории (за визит; альтернатива самостоятельному отбору)"}
    for k in LAB:
        w(f"| {names[k]} | {rsd(LAB[k]['low'])} | {rsd(LAB[k]['mid'])} | {rsd(LAB[k]['high'])} | [допущение] не найдено; заменить прайсом лаборатории |")
    w(f"| Стерильная бутыль 250 мл с тиосульфатом (за шт.) | {rsd(BOTTLE_STERILE['low'])} | {rsd(BOTTLE_STERILE['mid'])} | {rsd(BOTTLE_STERILE['high'])} | [web] Buddeberg 143,20 EUR без НДС / 170,41 EUR с НДС за 108 шт.; высокий - [допущение] |")
    w(f"| Прочие расходники на пробу (бутыль 1,5 л, лёд, перчатки, спирт, этикетка) | {rsd(CONSUMABLE_OTHER['low'])} | {rsd(CONSUMABLE_OTHER['mid'])} | {rsd(CONSUMABLE_OTHER['high'])} | [допущение] |")
    w(f"| Рейс до лаборатории ({TRIP_KM_ROUNDTRIP} км, {TRIP_HOURS:g} ч) | {rsd(trip_cost('low'))} | {rsd(trip_cost('mid'))} | {rsd(trip_cost('high'))} | [допущение]: {KM_COST['low']:g}/{KM_COST['mid']:g}/{KM_COST['high']:g} RSD/км, час {rsd(HOUR_COST['low'])}/{rsd(HOUR_COST['mid'])}/{rsd(HOUR_COST['high'])} RSD |")
    w("")
    w(f"Режим: кластер до {CLUSTER_MAX} аппаратов (зоны BVK: {ZONES}); микробиология на точку раз в {ROUTINE_INTERVAL_MONTHS[1]} мес (N=1) или раз в {ROUTINE_INTERVAL_MONTHS[5]} мес (N>=5) "
      f"по 2 пробы (вода насадки + смыв насадки); короткая химия - раз в {CHEM_SHORT_INTERVAL_MONTHS} мес на кластер; полный анализ - {FULL_PER_CLUSTER_PER_YEAR} раз в год на кластер; "
      f"внеплановых событий {UNPLANNED_PER_POINT_PER_YEAR:g} на точку в год ({UNPLANNED_MICRO} микро + {UNPLANNED_PHYS} химия на событие); {POINTS_PER_TRIP} точки за рейс. "
      "Обоснование - `docs/sampling/scaling.md`, `program.md`.\n")

    w("## 2. Стоимость одной пробы (RSD, лаборатория + расходники)\n")
    w("| Проба | Низкий | Средний | Высокий |")
    w("|---|---:|---:|---:|")
    for label, (m, p, mt) in (("Микро-пакет (1 бутыль)", (1, 0, 0)), ("Короткая физико-химия", (0, 1, 0)),
                              ("Расширенные металлы", (0, 0, 1)), ("Рутинный визит (2 микро: вода + смыв насадки)", (2, 0, 0)),
                              ("Полный анализ точки (микро + химия + металлы)", (1, 1, 1))):
        cells = []
        for s in SCEN:
            lab, cons = analysis_cost(s, m, p, mt)
            cells.append(rsd(lab + cons))
        w(f"| {label} | {' | '.join(cells)} |")
    w("")

    w("## 3. Разовые расходы запуска (пробы до выдачи воды + пересъёмка после промывки)\n")
    w("| N точек | Низкий | Средний | Высокий | Проб микро / химия / металлы / визитов (всего) |")
    w("|---:|---:|---:|---:|---|")
    for n in (1, 5, 20, 50):
        row = [launch_cost(n, s) for s in SCEN]
        r = row[1]
        w(f"| {n} | {rsd(row[0]['total'])} | {rsd(r['total'])} | {rsd(row[2]['total'])} | {r['micro']:g} / {r['phys']:g} / {r['metals']:g} / {r['visits']:g} |")
    w("")
    eq = equipment_total()
    w("## 4. Приборы и наборы (разово, на комплект пробоотборника)\n")
    w("| Позиция | RSD | Источник |")
    w("|---|---:|---|")
    for name, val, src in EQUIPMENT:
        w(f"| {name} | {rsd(val)} | {src} |")
    w(f"| **Итого** | **{rsd(eq)}** | один комплект на оператора; цены eBay/зарубежных магазинов, без НДС/доставки/пошлины, [уточнить] у местного дистрибьютора (Hanna, Сербия) |")
    w("")
    w(EQUIPMENT_NOTE_EXTRA + "\n")

    w("## 5. Месячная и годовая стоимость в установившемся режиме (RSD)\n")
    w("| N | Сценарий | Лаборатория | Расходники | Транспорт/время | **В месяц** | **В год** | На точку в месяц | Доля от пост. расходов точки (37 050/мес) |")
    w("|---:|---|---:|---:|---:|---:|---:|---:|---:|")
    for n in (1, 5, 20, 50):
        for s in SCEN:
            c = monthly_cost(n, s)
            per_point = c["total"] / n
            w(f"| {n} | {SCEN_RU[s]} | {rsd(c['lab'])} | {rsd(c['cons'])} | {rsd(c['transport'])} | **{rsd(c['total'])}** | **{rsd(c['total'] * 12)}** | {rsd(per_point)} | {per_point / FIXED_MONTHLY_SITE_RSD * 100:.1f}% |")
    w("")
    w("Первый год = запуск (раздел 3) + 12 месяцев установившегося режима + приборы (раздел 4); для N=1 в первые 3 месяца частота микробиологии та же (1 раз в месяц).\n")
    w("| N | Сценарий | Первый год, RSD | В EUR |")
    w("|---:|---|---:|---:|")
    for n in (1, 5, 20, 50):
        for s in SCEN:
            first = launch_cost(n, s)["total"] + monthly_cost(n, s)["total"] * 12 + eq * math.ceil(n / 20)
            w(f"| {n} | {SCEN_RU[s]} | {rsd(first)} | {first / EUR_TO_RSD:,.0f} |".replace(",", " "))
    w("")
    w("Для сравнения: подход «полная программа на каждой точке» (микро + химия + металлы раз в месяц на точку):\n")
    w("| N | Средний сценарий, RSD/мес | Выбранное правило, RSD/мес | Экономия |")
    w("|---:|---:|---:|---:|")
    for n in (1, 5, 20, 50):
        lab, cons = analysis_cost("mid", n, n, n)
        full_all = lab + cons + math.ceil(n / POINTS_PER_TRIP) * trip_cost("mid")
        sel = monthly_cost(n, "mid")["total"]
        w(f"| {n} | {rsd(full_all)} | {rsd(sel)} | {(1 - sel / full_all) * 100:.0f}% |")
    w("")

    w("## 6. Чувствительность (средний сценарий, RSD/мес)\n")
    w("### 6.1 Частота плановой микробиологии на точку\n")
    w("| N | раз в 1 мес | раз в 2 мес | раз в 3 мес |")
    w("|---:|---:|---:|---:|")
    for n in (1, 5, 20, 50):
        w(f"| {n} | " + " | ".join(rsd(monthly_cost(n, 'mid', interval=i)["total"]) for i in (1, 2, 3)) + " |")
    w("\n### 6.2 Цена анализов (множитель к лабораторным пакетам)\n")
    w("| N | x0,5 | x1 | x2 | x3 |")
    w("|---:|---:|---:|---:|---:|")
    for n in (1, 5, 20, 50):
        w(f"| {n} | " + " | ".join(rsd(monthly_cost(n, 'mid', price_mult=m)["total"]) for m in (0.5, 1, 2, 3)) + " |")
    w("\n### 6.3 Отбор силами лаборатории вместо самостоятельного\n")
    w("| N | Самостоятельно | Выезд лаборатории |")
    w("|---:|---:|---:|")
    for n in (1, 5, 20, 50):
        w(f"| {n} | {rsd(monthly_cost(n, 'mid')['total'])} | {rsd(monthly_cost(n, 'mid', lab_sampling=True)['total'])} |")
    w("\n### 6.4 Частота внеплановых событий на точку в год\n")
    w("| N | 0,5 | 1 | 2 | 4 |")
    w("|---:|---:|---:|---:|---:|")
    for n in (1, 5, 20, 50):
        w(f"| {n} | " + " | ".join(rsd(monthly_cost(n, 'mid', unplanned=u)["total"]) for u in (0.5, 1, 2, 4)) + " |")
    w("\n### 6.5 Размер кластера (влияет на число проб химии)\n")
    saved = CLUSTER_MAX
    w("| N | кластер 5 | кластер 10 | кластер 20 |")
    w("|---:|---:|---:|---:|")
    for n in (20, 50):
        cells = []
        for cm in (5, 10, 20):
            CLUSTER_MAX = cm
            cells.append(rsd(monthly_cost(n, "mid")["total"]))
        w(f"| {n} | " + " | ".join(cells) + " |")
    CLUSTER_MAX = saved
    w("")

    w("## 7. Что даст экономию\n")
    w("- **Кластеры** (химия по источнику воды и конфигурации, а не по каждой точке): химия и металлы зависят от числа кластеров K, а не N.")
    w("- **Реже плановая микробиология** (раз в 2-3 мес) после серии чистых результатов и без тревог телеметрии (раздел 6.1) - но не реже раза в квартал на точку.")
    w("- **Телеметрия** (EC/TDS, температура бака, литры, простой) переводит часть внеплановых проб в проверки приборами (EC-метр ~7 900-18 600 RSD один раз) и не заменяет лабораторию.")
    w("- **Групповые рейсы** (до 4 точек за рейс) вместо отдельных поездок; общие бутыли и заказ партиями.")
    w("- **Торг по абонементу** с лабораторией (годовой договор, скидка за объём) - [уточнить] у лаборатории.\n")

    w("## 8. Расход стерильных бутылей и точка заказа (поставка 8 дней)\n")
    w("Формула: точка заказа ROP = дневной расход x (срок поставки + страховой запас). Срок поставки 8 дней - пример владельца, "
      "страховой запас 7 дней - [допущение]. Расход = число микро-проб в месяц / 30 (установившийся режим).\n")
    w("| N | Микро-проб/мес | Расход/день | ROP (8+7 дн.), шт. |")
    w("|---:|---:|---:|---:|")
    for n in (1, 5, 20, 50):
        daily, rop = reorder_table(n)
        w(f"| {n} | {monthly_events(n)['micro']:.1f} | {daily:.2f} | {math.ceil(rop)} |")
    w("\nРасход при запуске 20 точек (по 2 точки в неделю; на запуск точки - 7 микро-бутылей, потом рутина):\n")
    w("| Неделя | Запущено за неделю | Всего точек | Бутылей за неделю |")
    w("|---:|---:|---:|---:|")
    for wk, new, tot, use in weekly_use():
        w(f"| {wk} | {new} | {tot} | {use:.1f} |")
    w("")
    for title, (st0, q1) in (("Вариант A: маленькая первая партия (остаток 14 шт., заказ 20 шт.)", (14, 20)),
                             ("Вариант B: первая партия 60 шт. (остаток 14 шт.)", (14, 60))):
        rop, mn, ev = simulate_orders(st0, q1)
        w(f"### {title}\n")
        w(f"ROP = пиковый расход/день x (8 + 7 дней запаса) = {rop} шт.; минимальный остаток за 14 недель: {mn} шт.\n")
        for e in ev:
            w(f"- {e}")
        w("")
    path = os.path.join("docs", "sampling", "costs.md")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print(f"written {path}")
    for n in (1, 5, 20, 50):
        print(n, [rsd(monthly_cost(n, s)["total"]) for s in SCEN])


if __name__ == "__main__":
    main()
