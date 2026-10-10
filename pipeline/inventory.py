"""Модель запаса с учётом срока поставки (дорожка sourcing-economics).

Запуск из корня репозитория: python3 pipeline/inventory.py
Пишет docs/economics/inventory-model.md.

Общая модель для расходников и запчастей; функции reorder_point и order_quantity
можно использовать для любых позиций (например, тара и наборы для проб, дорожка sampling).
Правило владельца: ненайденные входы = None («не найдено»); пример ниже — иллюстрация формулы.
"""

import math
import os


OUT = "docs/economics/inventory-model.md"

# Параметры метода — ПРЕДЛОЖЕНИЕ методики, не факт; утвердить владельцу.
SERVICE_LEVEL = 0.95        # целевая доля циклов без дефицита для позиций по отказам
SAFETY_DAYS_MIN = 7         # минимальный страховой запас расходников, суток
SAFETY_LEAD_SHARE = 0.25    # или доля срока поставки, что больше
COVER_DAYS = 90             # на сколько суток заказывается партия
MIN_ONHAND_CRITICAL = 1     # критичная позиция: всегда >=1 шт. на складе

# Транзит по каналам, найденный на страницах форвардера (индикативно): https://goodhopefreight.com/serbia.html
# море LCL 40–55 сут, FCL 35–50, авиа 5–10, экспресс 3–7. Сроки локальной и европейской поставки — не найдено.
TRANSIT_FOUND = {"Китай море (LCL)": "40–55", "Китай море (FCL)": "35–50", "Китай авиа": "5–10", "Китай экспресс": "3–7",
                 "локально (Сербия)": None, "ЕС (курьер/груз)": None}

NF = "не найдено"

# Позиции запаса. Цены, интервалы замены, интенсивности отказов, MOQ, сроки годности и поставки в открытых
# источниках не найдены -> None. Из найденного: платёжный модуль Nayax VPOS Touch 399 USD (США, shop.nayax.com).
PARTS = [
    dict(key="prefilter", name="Картриджи предфильтра", group="расходники", price=None, per=None, mode="consumable", interval=None, shelf=None, moq=None, critical=False, note="число на аппарат и интервал замены не найдены (EC-25)"),
    dict(key="membrane", name="RO-мембрана", group="расходники", price=None, per=None, mode="consumable", interval=None, shelf=None, moq=None, critical=True, note="цена мембраны 400 GPD и срок службы не найдены (EC-25)"),
    dict(key="uv", name="УФ-лампа", group="расходники", price=None, per=None, mode="consumable", interval=None, shelf=None, moq=None, critical=True, note="цена и ресурс не найдены (EC-25)"),
    dict(key="pump", name="Повышающий насос", group="запчасти", price=None, per=None, mode="failure", rate=None, shelf=None, moq=None, critical=True, note="цена и интенсивность отказов не найдены (EC-25)"),
    dict(key="payment", name="Платёжный модуль", group="запчасти", price=None, per=None, mode="failure", rate=None, shelf=None, moq=None, critical=True, note="найден листинг Nayax VPOS Touch 399 USD (https://shop.nayax.com/vpos-touch.html, версия для США, 5–14 шт. 314 USD, 15–19 шт. 289 USD, +9,99 USD/мес); европейская версия и отказы не найдены (EC-25)"),
    dict(key="sensors", name="Датчики и реле (комплект)", group="запчасти", price=None, per=None, mode="failure", rate=None, shelf=None, moq=None, critical=False, note="не найдено (EC-25)"),
    dict(key="heater", name="Обогреватель", group="запчасти", price=None, per=None, mode="failure", rate=None, shelf=None, moq=None, critical=False, note="не найдено (EC-25)"),
    dict(key="panel", name="Панели/замки корпуса", group="корпус", price=None, per=None, mode="failure", rate=None, shelf=None, moq=None, critical=False, note="не найдено (EC-25)"),
]

# ИЛЛЮСТРАЦИЯ формулы: все числа условные, не факты и не оценки реальной позиции.
EXAMPLE_PART = dict(key="example", name="Условная расходная позиция", group="иллюстрация", price=None, per=3, mode="consumable",
                    interval=90, shelf=None, moq=1, critical=False, note="числа условные")


def daily_demand(part, machines):
    if part["mode"] == "consumable":
        return machines * part["per"] / part["interval"]
    return machines * part["per"] * part["rate"] / 365.0


def poisson_quantile(mean, level):
    """Наименьшее s, при котором P(X<=s) >= level для Пуассона со средним mean."""
    if mean <= 0:
        return 0
    s, term, cum = 0, math.exp(-mean), math.exp(-mean)
    while cum < level and s < 10000:
        s += 1
        term *= mean / s
        cum += term
    return s


def reorder_point(part, machines, lead_days):
    """Точка заказа по позиции запаса (на складе + в пути) и страховой запас."""
    d = daily_demand(part, machines)
    mean = d * lead_days
    if part["mode"] == "consumable":
        ss = d * max(SAFETY_DAYS_MIN, SAFETY_LEAD_SHARE * lead_days)
        rop = math.ceil(mean + ss)
    else:
        q = poisson_quantile(mean, SERVICE_LEVEL)
        rop = q
        ss = q - mean
    if part["critical"]:
        rop = max(rop, MIN_ONHAND_CRITICAL)
    return rop, max(0.0, rop - mean), d


def initial_stock(part, machines, lead_days):
    """Запас на старте: расходник — ROP + Q (первая партия); запчасть по отказам — ROP, округлённый вверх до MOQ."""
    rop, _, _ = reorder_point(part, machines, lead_days)
    if part["mode"] == "consumable":
        return rop + order_quantity(part, machines)
    return 0 if rop == 0 else max(rop, part["moq"])


def order_quantity(part, machines, cover_days=COVER_DAYS):
    d = daily_demand(part, machines)
    q = max(part["moq"], math.ceil(d * cover_days))
    if part["shelf"]:
        q = min(q, max(part["moq"], math.floor(d * part["shelf"] * 0.8)))  # не заказывать то, что не успеть использовать до срока годности
    return q


def fmt(v, d=0):
    return f"{v:,.{d}f}".replace(",", " ")


def simulate(part, ramp, lead, lot, days=42, start_stock=12):
    """Пошаговый пример: парк растёт, партия в пути, вторая заказывается до прихода первой.
    ramp — {день: число аппаратов}. Возвращает строки таблицы."""
    machines = ramp[0]
    onhand = float(start_stock)
    pipeline = []   # (день прихода, шт)
    rows = []
    for day in range(days + 1):
        arrived = sum(q for t, q in pipeline if t == day)
        pipeline = [(t, q) for t, q in pipeline if t != day]
        onhand += arrived
        if day in ramp:
            machines = ramp[day]
        onorder = sum(q for _, q in pipeline)
        rop, _, d = reorder_point(part, machines, lead)
        action = ""
        if arrived:
            action = f"пришла партия {arrived:.0f}"
        if onhand + onorder <= rop:
            q = lot
            pipeline.append((day + lead, q))
            action = (action + "; " if action else "") + f"ЗАКАЗ {q}, придёт на сутки {day + lead}"
            onorder += q
        rows.append((day, machines, d, rop, onhand, onorder, onhand + onorder, action))
        onhand -= d
    return rows


def main():
    L = []
    L.append("# Модель запаса с учётом сроков поставки\n")
    L.append("Сгенерировано `pipeline/inventory.py` (`python3 pipeline/inventory.py` из корня репозитория). Метки: «не найдено» — вход неизвестен (ID в `docs/reports/unknowns-and-open-issues.md`); параметры метода — предложение методики, не факт. Прежние таблицы позиций, точек заказа и капитала в запасе для 1/5/20 аппаратов удалены: они опирались на выдуманные цены, интервалы замены, отказы и сроки поставки.\n")
    L.append("## 1. Формулы\n")
    L.append("Обозначения: N — число аппаратов, d — суточный расход, L — срок поставки (сутки), SS — страховой запас, ROP — точка заказа, Q — размер партии, S — позиция запаса.\n")
    L.append("- Расход расходника: d = N × k / T, где k — штук на аппарат, T — интервал замены, сутки.")
    L.append("- Расход по отказам: d = N × k × r / 365, где r — доля отказов в год.")
    L.append("- **Позиция запаса** S = на складе + в пути.")
    L.append(f"- **Точка заказа** ROP = d × L + SS. Расходник: SS = d × max({SAFETY_DAYS_MIN} сут, {SAFETY_LEAD_SHARE:.0%} × L). Позиция по отказам: ROP — {SERVICE_LEVEL:.0%}-квантиль распределения Пуассона со средним d × L. Числа {SAFETY_DAYS_MIN} сут, {SAFETY_LEAD_SHARE:.0%}, {SERVICE_LEVEL:.0%} — предложение методики, владельцу утвердить.")
    L.append(f"- Критичные позиции (мембрана, УФ, насос, платёжный модуль): ROP не меньше {MIN_ONHAND_CRITICAL} шт. Обоснование: простой точки стоит p × N_день рублей выручки в сутки (p = 10 RSD/л по решению владельца; N — объём, не найден).")
    L.append("- **Правило заказа:** когда S <= ROP, заказать партию Q. Сравнивается позиция (склад + в пути), а не остаток на складе.")
    L.append(f"- **Партия** Q = max(MOQ, d × {COVER_DAYS} сут), не больше 80% от d × срок годности (предложение методики).")
    L.append("- Запас на старте: расходник — ROP + Q; запчасть по отказам — ROP (при ROP > 0 не меньше MOQ).\n")
    L.append("## 2. Позиции: входы\n")
    L.append("| Позиция | Цена | Расход | Срок годности | MOQ | Критичная | Примечание |")
    L.append("|---|---|---|---|---|---|---|")
    for p in PARTS:
        L.append(f"| {p['name']} | {NF} | {NF} | {NF} | {NF} | {'да' if p['critical'] else 'нет'} | {p['note']} |")
    L.append("")
    L.append("Сроки поставки по каналам: найден только транзит (форвардер, индикативно, без даты): " + "; ".join(f"{k} — {v} сут" for k, v in TRANSIT_FOUND.items() if v) + ". Срок для локальной и европейской поставки, производства и оформления: " + NF + " (EC-19). ROP и запас для реальных позиций **не определены**.\n")
    L.append("## 3. ИЛЛЮСТРАЦИЯ формулы, числа условные: срок поставки 8 суток, парк растёт, первая партия в пути\n")
    cart = EXAMPLE_PART
    lead = 8
    ramp = {0: 5, 2: 10, 4: 15, 6: 20}
    L.append(f"Это иллюстрация логики правила, а не прогноз: условная позиция ({cart['per']} шт. на аппарат, замена раз в {cart['interval']} сут), срок поставки L = {lead} сут, парк 5 аппаратов с 0-х суток, затем +5 в сутки 2, 4, 6, пробная партия 6 шт., стартовый остаток 3 шт. Все эти числа выбраны для показа механики и не относятся к реальным закупкам.\n")
    start_stock_example = 3
    rows = simulate(cart, ramp, lead, lot=6, days=30, start_stock=start_stock_example)
    L.append("| Сутки | Аппаратов | Расход, шт./сут | ROP | На складе | В пути | Позиция | Действие |")
    L.append("|---|---|---|---|---|---|---|---|")
    shown = [r for r in rows if r[7] or r[0] % 7 == 0]
    for day, m, d, rop, oh, oo, pos, act in shown:
        L.append(f"| {day} | {m} | {d:.2f} | {rop} | {oh:.1f} | {oo:.0f} | {pos:.1f} | {act} |")
    L.append("")
    orders = [r for r in rows if "ЗАКАЗ" in r[7]]
    L.append("Разбор (для условных чисел):")
    if len(orders) >= 2:
        first, second = orders[0], orders[1]
        arrival_first = first[0] + lead
        flag = "до прихода первой" if second[0] < arrival_first else "после прихода первой"
        L.append(f"- Первый заказ — сутки {first[0]} (придёт на сутки {arrival_first}); второй — сутки {second[0]}, то есть **{flag}** партии: ROP растёт вместе с парком, позиция (склад + в пути) снова опускается до ROP.")
    L.append("- Правило не требует ждать прихода первой партии: заказ определяется позицией и ROP, пересчитанной на текущий парк.")
    short = min((r[4] - r[2] for r in rows), default=0)
    need = next((st for st in range(start_stock_example, start_stock_example + 20)
                 if min(r[4] - r[2] for r in simulate(cart, ramp, lead, lot=6, days=30, start_stock=st)) >= 0), None)
    if short >= 0:
        L.append(f"- Минимальный остаток на конец суток: {short:.1f} шт. (дефицита нет).")
    else:
        L.append(f"- Минимальный остаток на конец суток: {short:.1f} шт. — кратковременный дефицит перед приходом первой партии: парк вырос быстрее, чем успел вырасти заказ. Дефицит исчезает при стартовом остатке {need} шт. — иллюстрация вывода: при быстрой раскатке стартовый запас считать по конечному парку.")
    L.append("- Шаблон для своих данных: изменить `ramp`, `lead`, `lot` в `simulate()` и позиции в `PARTS`.\n")
    L.append("## 4. Практика хранения\n")
    L.append("Срок годности картриджей и мембран, условия хранения, MOQ, площадь склада: " + NF + " (EC-26); спросить поставщиков. Пересмотр: после первых данных пилота подставить интервалы замены и отказы в `PARTS` и перезапустить скрипт. Модель общая: для тары и наборов для проб (дорожка sampling) достаточно добавить позиции в `PARTS`.")
    L.append("")
    os.makedirs("docs/economics", exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L) + "\n")
    print(f"Создан {OUT}")
    print("Пример (условные числа), заказы на сутки", [r[0] for r in rows if "ЗАКАЗ" in r[7]])
    print("Входы реальных позиций не найдены: ROP/капитал не считаются")


if __name__ == "__main__":
    main()
