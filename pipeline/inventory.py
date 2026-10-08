"""Модель запаса с учётом срока поставки (дорожка sourcing-economics).

Запуск из корня репозитория: python3 pipeline/inventory.py
Пишет docs/economics/inventory-model.md.

Общая модель для расходников и запчастей; функции reorder_point и order_quantity
можно использовать для любых позиций (например, тара и наборы для проб, дорожка sampling).
Метки: [repo] путь, [web] URL, [заполнитель] — значение без найденного источника, заменить данными.
"""

import math
import os

from fx import EUR_TO_RSD, USD_TO_RSD

OUT = "docs/economics/inventory-model.md"

SERVICE_LEVEL = 0.95        # доля циклов без дефицита для позиций по отказу [заполнитель]
SAFETY_DAYS_MIN = 7         # минимальный страховой запас расходников, суток [заполнитель]
SAFETY_LEAD_SHARE = 0.25    # или доля срока поставки, что больше
COVER_DAYS = 90             # на сколько суток заказывается партия, если нет иных ограничений
MIN_ONHAND_CRITICAL = 1     # критичная позиция: всегда ≥1 шт. на складе (простой точки дороже хранения)
REVENUE_PER_DAY_RSD = 80 * 10  # потери от простоя точки при 80 л/день × 10 RSD/л [repo] решение 0004

# Срок поставки по каналам, сутки. Транзит: [web] goodhopefreight.com/serbia.html (море 35–55, авиа 5–10,
# экспресс 3–7); остальное — [заполнитель], уточнить у поставщиков.
CHANNELS = {
    "локально (Сербия)": 3,
    "ЕС (курьер/груз)": 10,
    "Китай экспресс": 14,
    "Китай море": 60,
}

# mode: "consumable" — расход по интервалу замены (сутки); "failure" — расход по отказам (доля в год на штуку)
PARTS = [
    dict(key="prefilter", name="Картриджи предфильтра", group="расходники", price=25.0,
         src="[repo] FINANCE 3.4 (20–40 EUR, замена раз в 3 мес)", per=3, mode="consumable", interval=90,
         shelf=730, moq=10, channel="локально (Сербия)", critical=False,
         note="число картриджей на аппарат (3) — [заполнитель]; TECH_SPEC: 5–7 ступеней, факт 0004"),
    dict(key="membrane", name="RO-мембрана", group="расходники", price=120.0,
         src="[web] ориентир: 4040-мембраны 119–500 USD (класс больше, чем 400 GPD) https://smartbuy.alibaba.com/buyingguides/membranes-bw30-4040; цена мембраны 400 GPD не найдена, [уточнить] у поставщика",
         per=1, mode="consumable", interval=730, shelf=1095, moq=1, channel="ЕС (курьер/груз)", critical=True,
         note="срок службы 2 года — [заполнитель], зависит от воды и обслуживания"),
    dict(key="uv", name="УФ-лампа", group="расходники", price=30.0,
         src="[заполнитель]; найден только полный УФ-блок 40 Вт — 157 EUR (выдача ebay.de, без прямой ссылки), лампа отдельно не найдена",
         per=1, mode="consumable", interval=365, shelf=None, moq=1, channel="ЕС (курьер/груз)", critical=True,
         note="замена раз в год — типовое правило, [уточнить] у поставщика УФ"),
    dict(key="pump", name="Повышающий насос", group="запчасти", price=50.0,
         src="[web] 10–12 USD оптом (MOQ 2) до 39–90 GBP розница; середина — [заполнитель]",
         per=1, mode="failure", rate=0.15, shelf=None, moq=1, channel="ЕС (курьер/груз)", critical=True,
         note="интенсивность отказов 15%/год — [заполнитель], собирать статистику пилота"),
    dict(key="payment", name="Платёжный модуль", group="запчасти", price=365.0,
         src="[web] Nayax VPOS Touch 399 USD https://shop.nayax.com/vpos-touch.html (≈365 EUR)",
         per=1, mode="failure", rate=0.05, shelf=None, moq=1, channel="ЕС (курьер/груз)", critical=True,
         note="отказ или кража; 5%/год — [заполнитель]"),
    dict(key="sensors", name="Датчики и реле (комплект)", group="запчасти", price=25.0,
         src="[repo] TECH_SPEC §9.3: датчики 5+5+5+3 EUR, GSM 5 EUR",
         per=1, mode="failure", rate=0.10, shelf=None, moq=5, channel="Китай экспресс", critical=False,
         note="10%/год — [заполнитель]"),
    dict(key="heater", name="Обогреватель", group="запчасти", price=80.0,
         src="[repo] TECH 1.8", per=1, mode="failure", rate=0.10, shelf=None, moq=1, channel="ЕС (курьер/груз)",
         critical=False, note="отказ или кража; 10%/год — [заполнитель]"),
    dict(key="panel", name="Панели/замки корпуса", group="корпус", price=60.0,
         src="[заполнитель]; антивандальная защита 350 EUR целиком [repo] TECH 1.10",
         per=1, mode="failure", rate=0.20, shelf=None, moq=1, channel="локально (Сербия)", critical=False,
         note="вандализм; 20%/год — [заполнитель]"),
]


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
    L.append("Сгенерировано `pipeline/inventory.py` (`python3 pipeline/inventory.py` из корня репозитория). Общая модель для компонентов, расходников и (дорожка sampling) тары и наборов для проб: достаточно задать позиции в `PARTS`. Метки: [repo], [web], [заполнитель] — значение без найденного источника.\n")
    L.append("## 1. Формулы\n")
    L.append("Обозначения: N — число аппаратов, d — суточный расход, L — срок поставки (сутки), SS — страховой запас, ROP — точка заказа, Q — размер партии, S — позиция запаса.\n")
    L.append("- Расход расходника: d = N × k / T, где k — штук на аппарат, T — интервал замены, сутки.")
    L.append("- Расход по отказам (запчасти): d = N × k × r / 365, где r — доля отказов в год.")
    L.append("- **Позиция запаса** S = на складе + в пути (заказано, но не пришло) − отложенный спрос.")
    L.append(f"- **Точка заказа** ROP = d × L + SS. Расходник: SS = d × max({SAFETY_DAYS_MIN} сут, {SAFETY_LEAD_SHARE:.0%} × L). Позиция по отказам: ROP — {SERVICE_LEVEL:.0%}-квантиль распределения Пуассона со средним d × L (SS = ROP − d × L).")
    L.append(f"- Критичные позиции (мембрана, УФ, насос, платёжный модуль): ROP не меньше {MIN_ONHAND_CRITICAL} шт. Обоснование: простой точки стоит ≈{fmt(REVENUE_PER_DAY_RSD)} RSD выручки в сутки при 80 л/день [repo, решение 0004], а хранение одной запчасти — доли процента в день.")
    L.append(f"- **Правило заказа:** когда S ≤ ROP, заказать партию Q. Сравнивается позиция (склад + в пути), а не остаток на складе: иначе вторая партия закажется сразу же, пока первая в пути, и запас раздуется.")
    L.append(f"- **Партия** Q = max(MOQ, d × {COVER_DAYS} сут), не больше 80% от d × срок годности (чтобы не заказывать то, что не успеют использовать).")
    L.append("- Запас на старте: расходник — ROP + Q (первая партия); запчасть по отказам — ROP (при ROP > 0, не меньше MOQ), дальше пополняется партией Q после первого расхода.")
    L.append("- Если срок поставки растёт (например, море вместо экспресса), ROP пересчитывается по новому L, и позиции в пути не отменяются.\n")

    L.append("## 2. Позиции и допущения\n")
    L.append("| Позиция | Цена, EUR | Источник цены | Расход | Срок годности, сут | MOQ | Канал, срок L | Критичная | Примечание |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for p in PARTS:
        use = f"{p['per']} шт./{p['interval']} сут" if p["mode"] == "consumable" else f"{p['rate']:.0%}/год"
        L.append(f"| {p['name']} | {p['price']:.0f} | {p['src']} | {use} | {p['shelf'] or '—'} | {p['moq']} | {p['channel']}, {CHANNELS[p['channel']]} сут | {'да' if p['critical'] else 'нет'} | {p['note']} |")
    L.append("")
    L.append("Каналы и сроки: " + "; ".join(f"{k} — {v} сут" for k, v in CHANNELS.items()) + ". Море/экспресс/авиа [web] https://goodhopefreight.com/serbia.html; остальное — [заполнитель], уточнить у поставщиков.\n")

    L.append("## 3. Пример: срок поставки 8 суток, парк растёт, первая партия ещё в пути\n")
    cart = PARTS[0]
    lead = 8
    ramp = {0: 5, 2: 10, 4: 15, 6: 20}
    L.append(f"Позиция: {cart['name']} ({cart['per']} шт. на аппарат, замена раз в {cart['interval']} сут), срок поставки L = {lead} сут. Парк растёт быстро: 5 аппаратов с 0-х суток, затем +5 в сутки 2, 4, 6 (монтаж серии). Партия — пробная, 6 шт. (поставщик отгружает малыми лотами на старте; обычная партия Q — в §4). Стартовый остаток 3 шт.\n")
    rows = simulate(cart, ramp, lead, lot=6, days=30, start_stock=3)
    L.append("| Сутки | Аппаратов | Расход, шт./сут | ROP | На складе | В пути | Позиция | Действие |")
    L.append("|---|---|---|---|---|---|---|---|")
    shown = [r for r in rows if r[7] or r[0] % 7 == 0]
    for day, m, d, rop, oh, oo, pos, act in shown:
        L.append(f"| {day} | {m} | {d:.2f} | {rop} | {oh:.1f} | {oo:.0f} | {pos:.1f} | {act} |")
    L.append("")
    orders = [r for r in rows if "ЗАКАЗ" in r[7]]
    L.append("Разбор:")
    if len(orders) >= 2:
        first, second = orders[0], orders[1]
        arrival_first = first[0] + lead
        flag = "до прихода первой" if second[0] < arrival_first else "после прихода первой"
        L.append(f"- Первый заказ — сутки {first[0]} (придёт на сутки {arrival_first}); второй — сутки {second[0]}, то есть **{flag}** партии: парк вырос, ROP вырос, а позиция (склад + в пути) снова опустилась до ROP.")
    L.append("- Правило не требует ждать прихода первой партии: заказ определяется позицией (склад + в пути) и ROP, пересчитанной на текущий парк.")
    L.append("- Если заказ не сделать, дефицит возникает через (остаток − ROP)/d суток после пересечения ROP; страховой запас покрывает отклонения расхода и срока.")
    short = min((r[4] for r in rows), default=0)
    L.append(f"- Минимальный остаток на складе за период: {short:.1f} шт. ({'дефицита нет' if short >= 0 else 'ДЕФИЦИТ'}).")
    L.append("- Шаблон для своих данных: изменить `ramp`, `lead`, `lot` в `simulate()`.\n")

    L.append("## 4. Точки заказа и запас по группам для 1, 5 и 20 аппаратов\n")
    L.append("Запас на старте — по правилу из §1. Годовой расход в штуках и евро — для планирования бюджета.\n")
    totals = {}
    for n in (1, 5, 20):
        L.append(f"### {n} аппарат(ов)\n")
        L.append("| Позиция | d, шт./сут | L, сут | SS | ROP | Q | Запас на старте | Годовой расход, шт. | Капитал на старте, EUR |")
        L.append("|---|---|---|---|---|---|---|---|---|")
        cap_max = cap_avg = annual = 0.0
        for p in PARTS:
            ll = CHANNELS[p["channel"]]
            rop, ss, d = reorder_point(p, n, ll)
            q = order_quantity(p, n)
            mx = initial_stock(p, n, ll)
            yr = d * 365
            cmax = mx * p["price"]
            cap_max += cmax
            annual += yr * p["price"]
            L.append(f"| {p['name']} | {d:.3f} | {ll} | {ss:.1f} | {rop} | {q} | {mx} | {yr:.1f} | {fmt(cmax)} |")
        L.append(f"| **Итого** | | | | | | | | **{fmt(cap_max)}** |")
        L.append("")
        L.append(f"Годовые расходные материалы и запчасти по модели: ≈{fmt(annual)} EUR (≈{fmt(annual*EUR_TO_RSD)} RSD) на {n} аппарат(ов), то есть ≈{fmt(annual/n)} EUR на аппарат в год. Капитал в запасе на старте ≈{fmt(cap_max)} EUR (≈{fmt(cap_max*EUR_TO_RSD)} RSD).\n")
        totals[n] = (cap_max, cap_avg, annual)

    L.append("## 5. Влияние канала поставки на точку заказа (20 аппаратов)\n")
    L.append("| Позиция | Канал | L, сут | ROP | Q |")
    L.append("|---|---|---|---|---|")
    for key in ("prefilter", "uv", "membrane"):
        p = next(x for x in PARTS if x["key"] == key)
        for ch, ll in CHANNELS.items():
            rop, _, _ = reorder_point(p, 20, ll)
            q = order_quantity(p, 20)
            L.append(f"| {p['name']} | {ch} | {ll} | {rop} | {q} |")
    L.append("")
    L.append("Чем дольше канал, тем больше ROP; для критичных позиций при морской поставке (≈60 сут) выгодно держать запас или заказывать в ЕС/экспрессом.\n")

    L.append("## 6. Практика и срок хранения\n")
    L.append("- **Минимальные партии (MOQ)** задают реальный Q при малом парке: для датчиков MOQ 5 даёт запас на годы — брать комплект на 5 точек и делить между точками.")
    L.append("- **Срок годности:** картриджи и мембраны в упаковке хранить сухо, без мороза и света, срок хранения принят 730 и 1095 сут [заполнитель, уточнить у поставщика]; УФ-лампы, насосы, платёжные модули срока не имеют, но лампы расходуют ресурс только в работе.")
    L.append("- **Где хранить:** до 5 аппаратов — у техника/в кладовой (капитал в таблице выше); при 20 аппаратах нужен небольшой склад ≈ 2–4 м², отдельная строка «склад» в общих затратах (`financial_model.md`).")
    L.append("- **Пересмотр:** раз в квартал заменять допущения (интенсивность отказов, интервал замены) данными пилота и пересчитывать `python3 pipeline/inventory.py`.")
    L.append("- **Использование другими дорожками:** для тары и наборов для проб добавить позиции в `PARTS` с их расходом и сроком поставки, не меняя формул (дорожка sampling).")
    L.append("")
    os.makedirs("docs/economics", exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L) + "\n")
    print(f"Создан {OUT}")
    for n, (cm, ca, an) in totals.items():
        print(f"{n} аппарат(ов): капитал на старте {cm:,.0f} EUR, годовой расход {an:,.0f} EUR")
    print("Пример 8 суток: заказы на сутки", [r[0] for r in rows if "ЗАКАЗ" in r[7]])


if __name__ == "__main__":
    main()
