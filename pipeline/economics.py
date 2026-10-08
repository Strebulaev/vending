"""Финансовая модель водоматов и стоимость «от двери до двери» (дорожка sourcing-economics).

Запуск из корня репозитория: python3 pipeline/economics.py
Пишет: docs/economics/financial-model.md, ready-made-options-landed-cost.md, pricing-scenarios.md.

Модель опирается на pipeline/calculator.py (SCOPE, смета, тариф воды), его не меняет.
Все параметры в словарях вверху. Источники: [web] URL, [repo] путь, [заполнитель] —
число без найденного источника, подставлено, чтобы расчёт был замкнут; заменить котировкой.
"""

import math
import os

import calculator as calc
from fx import EUR_TO_RSD, USD_TO_RSD, to_eur

OUT_DIR = "docs/economics"

# ---------------------------------------------------------------------------
# 1. Параметры финансовой модели
# ---------------------------------------------------------------------------
PARAMS = {
    "price_per_l": calc.PRICE_PER_5L_RSD / 5,       # [repo] решение 0004
    "water_tariff_rsd_m3": calc.WATER_TARIFF_RSD_M3,  # [repo] факт 0003
    "reject_multiplier": calc.REJECT_MULTIPLIER,    # [repo] допущение calculator.py
    "payment_fee": calc.PAYMENT_FEE,                # [repo] calculator.py (1,5–3%)
    "tax_rate": calc.TAX_RATE,                      # [repo] calculator.py
    "rent_eur_base": 150.0,                         # [repo] бриф §3.1, LOCATIONS 5.1
    # Страхование: ориентир 86,27 EUR/год (пакет от кражи для малого бизнеса, Хорватия;
    # не Сербия, не аппарат) [web] https://ponuda.wiener.hr/EasyEdit/UserFiles/letci/2024-01/wiener/le-114-24-01obrtnici-i-poduzetniciwiener.pdf
    "insurance_eur_year": 86.27,
    # Анализы воды: цена не найдена, ожидает дорожки sampling/certification
    "lab_rsd_month": 0.0,
}

# Группы активов пилота (EUR). Суммы — строки смет TECH/INTEGRATION/LOCATIONS/IT/OPERATIONS [repo];
# сроки службы — [заполнитель], подтвердить у бухгалтера. Налоговые ставки Сербии: группы
# 2,5/10/15/20/30%, не перечисленное попадает в III группу 15% [web]
# https://kpmg.com/rs/sr/analize-i-istrazivanja/poreske-vesti/2018/12/usvojene-su-izmene-i-dopune-zakona-o-porezu-na-dobit-pravnih-lica.html
ASSET_GROUPS = [
    # (название, EUR, срок службы лет или None)
    ("RO-блок (базовый аппарат, FOB)", 915.0, 6),
    ("Корпус и антивандальная защита (шкаф)", 350.0, 8),
    ("Электроника (оплата, камера, GPS, датчики, обогреватель)", 875.0, 4),
    ("Сборка, интеграция, телеметрия", 1790.0, 6),
    ("Оборудование площадки (учёт, согласование)", 700.0, 3),
    ("Начальный склад запчастей (не амортизируется)", 800.0, None),
]
REINFORCED_EXTRA_PCT = 0.25   # [repo] TECH 1.10: усиленная защита +15–25% к цене аппарата
REINFORCED_THEFT_FACTOR = 0.5  # [заполнитель] усиленный корпус вдвое снижает риск

# Типы локаций: [заполнитель] до результатов дорожки hardware (docs/hardware/location-types.md)
LOCATION_TYPES = {
    "low-cost": dict(rent_x=0.5, lpd=40, theft=0.10, config="reinforced"),
    "premium": dict(rent_x=2.0, lpd=120, theft=0.03, config="standard"),
    "бизнес": dict(rent_x=1.5, lpd=100, theft=0.03, config="standard"),
    "амбициозная": dict(rent_x=3.0, lpd=200, theft=0.05, config="reinforced"),
}
THEFT_LOSS_EUR = 1500.0  # [заполнитель] средний ущерб от события: электроника 875 EUR + ремонт корпуса

SCENARIOS = {
    "консервативный": dict(lpd=50, price=10.0, rent_x=1.0, theft=0.10),
    "базовый": dict(lpd=80, price=10.0, rent_x=1.0, theft=0.05),
    "оптимистичный": dict(lpd=200, price=10.0, rent_x=1.0, theft=0.02),
}
# Общие (не связанные с размещением) затраты сети, EUR/мес. [заполнитель]: источника нет,
# значения для расчёта; уточнить у бухгалтера, юриста, подрядчика (см. REPORT.md, открытые вопросы)
SHARED_COSTS_EUR_MONTH = {
    "бухгалтерия и юристы": {1: 150, 5: 250, 20: 400},
    "документация, сертификаты, реестры": {1: 0, 5: 100, 20: 250},
    "маркетинг": {1: 0, 5: 200, 20: 600},
    "софт и платформа (общая часть)": {1: 0, 5: 100, 20: 300},
    "склад и логистика запчастей": {1: 0, 5: 100, 20: 300},
    "техник/координатор (доля ставки)": {1: 0, 5: 500, 20: 1500},
}

# ---------------------------------------------------------------------------
# 2. Параметры закупки «от двери до двери»
# ---------------------------------------------------------------------------
# Индексы случаев: 0 низ, 1 середина, 2 верх.
CASES = ("низ", "середина", "верх")
UNIT_CBM = 1.5      # [заполнитель] кубатура упакованного аппарата, запросить у поставщика
UNIT_KG = 200.0     # [заполнитель] вес брутто
RO_BASE_EUR = 915.0  # [repo] TECH 1.1 (1000 USD)

A = {
    # [web]+[repo]: 590–2000 USD FOB в объявлениях; 1000 USD в TECH_SPEC §9.3
    "price_usd": (590, 1000, 2000),
    "packing_eur": (80, 150, 250),            # [заполнитель] экспортная упаковка (часто включена в цену)
    "duty": (0.0, 0.05, 0.10),                # 10% — стандартная ставка упрощённой процедуры [web]
                                              # https://biznis.rs/preduzetnik/porezi/sta-se-sve-moze-uneti-u-srbiju-bez-carine/ ;
                                              # 0% возможна по CN–RS FTA с 01.07.2024 [web]
                                              # https://www.srbija.gov.rs/vest/en/226315/free-trade-agreement-between-serbia-peoples-republic-of-china-enters-into-force.php ;
                                              # ставка по 8421 21 НЕ НАЙДЕНА; 5% — середина диапазона для расчёта
    "warranty_pct": (0.03, 0.05, 0.08),       # [заполнитель] резерв на гарантию
}
# Фрахт Китай→Сербия. Ставки форвардера, без даты, ориентир (USD):
# https://goodhopefreight.com/serbia.html — LCL 160–290/м³ (40–55 сут), 20ft 3800–6200, 40ft 5200–8500 (35–50 сут),
# воздух 5–9/кг (5–10 сут, аэропорт–аэропорт), экспресс 10–18/кг (3–7 сут, дверь–дверь).
# Ж/д до Белграда, 40ft: 8850–9250 USD (июнь–август 2026, без пункта назначения), 18–25 сут:
# https://goodhopefreight.com/serbia/2026-freight.html ; ж/д LCL 150–400 USD/м³ без даты (sino-shipping.com).
FREIGHT = {
    "lcl_usd_cbm": (160, 225, 290),
    "fcl20_usd": (3800, 5000, 6200),
    "fcl40_usd": (5200, 6850, 8500),
    "rail_lcl_usd_cbm": (150, 275, 400),
    "rail_fcl40_usd": (8850, 9050, 9250),
    "air_usd_kg": (5, 7, 9),
    "express_usd_kg": (10, 14, 18),
    # Фиксированные сборы по концам и автовывоз из порта/терминала — НЕ НАЙДЕНЫ, [заполнитель] EUR за отправку
    "fixed_lcl_eur": (250, 400, 650),
    "fixed_fcl_eur": (500, 800, 1200),
    "inland_lcl_eur": (300, 450, 700),    # Копер/Бар → Белград, 631 км по дороге (rome2rio)
    "inland_fcl_eur": (800, 1100, 1500),
    "fixed_air_eur": (150, 300, 500),
}
TRANSIT_DAYS = {  # [web] goodhopefreight.com/serbia.html, /serbia/2026-freight.html
    "море (LCL)": "40–55", "море (FCL)": "35–50", "ж/д": "18–25", "авиа": "5–10", "экспресс": "3–7",
}
INSURANCE_RATE = (0.003, 0.004, 0.005)  # [web] 0,3–0,5% от стоимости CIF+10% https://gofreight.com/glossary/cargo-insurance
BROKER_EUR = (45, 150, 300)  # на отправку. Низ: DHL Сербия, импортное оформление 5 265 RSD [web]
                             # https://mydhl.express.dhl/rs/sr/ship/customs-services.html ; середина, верх — [заполнитель]
VAT = 0.20  # [web] НДС 20% на CIF+пошлина https://biznis.rs/preduzetnik/porezi/sta-se-sve-moze-uneti-u-srbiju-bez-carine/
INLAND_EUR = (50, 100, 200)    # [заполнитель] местная доставка до площадки за единицу
INSTALL_EUR = (100, 200, 400)  # [заполнитель] подключение воды/слива, разгрузка; учёт и интеграция в CAPEX пилота отдельно

B = {  # местный дистрибьютор: цена = k × 915 EUR [допущение, котировок нет], без НДС, доставка до Белграда включена
    "k": (1.5, 2.0, 2.5),
    "warranty_pct": (0.0, 0.02, 0.04),
}
D = {  # европейский поставщик: EXW, k × 915 EUR [допущение; Ecosoft и др.: «цена по запросу»]
    "k": (2.0, 3.0, 4.0),
    "packing_eur": (0, 50, 100),
    "pallet_eur": (150, 250, 400),     # [заполнитель] за паллет; перевозчики найдены (M&M Штутгарт–Белград, DHL Freight), цены нет
    "ftl_eur": (1200, 1800, 2500),     # [заполнитель] полная машина, при ≥10 аппаратов
    "warranty_pct": (0.01, 0.02, 0.04),
}
# Общий блок модулей (одинаков для A/B/D, в сравнение источников не входит): TECH_SPEC §9.3 + TECH 1.4–1.10 [repo]
MODULES_EUR = {
    "модуль безналичной оплаты": (150, 300, 450),
    "камера": (150, 150, 150),
    "GPS-трекер": (45, 60, 75),
    "датчики, GSM, геркон": (25, 72, 120),
    "обогреватель": (80, 80, 80),
    "антивандальная защита": (350, 350, 350),
    "интеграция и сборка": (500, 500, 500),
}
# Этапы срока поставки, суток [заполнитель], кроме транзита [web]
STAGES_DAYS = {
    "котировка, договор, аванс": (7, 10, 14),
    "производство/подготовка у поставщика": (15, 25, 40),
    "вывоз, экспортное оформление": (3, 5, 7),
    "ввозное оформление и подача деклараций": (2, 4, 7),
    "доставка до площадки, установка, приёмка": (3, 5, 10),
}


def usd(v):
    return v * USD_TO_RSD / EUR_TO_RSD


def rsd(v_eur):
    return v_eur * EUR_TO_RSD


def fmt(v, d=0):
    return f"{v:,.{d}f}".replace(",", " ")


# ---------------------------------------------------------------------------
# 3. Стоимость «от двери до двери»
# ---------------------------------------------------------------------------
def freight_a(route, n, c):
    """Возвращает (EUR за партию, описание режима)."""
    cbm = UNIT_CBM * n
    if route == "море":
        lcl = usd(FREIGHT["lcl_usd_cbm"][c]) * cbm + FREIGHT["fixed_lcl_eur"][c] + FREIGHT["inland_lcl_eur"][c]
        fcl_box = FREIGHT["fcl20_usd"] if cbm <= 28 else FREIGHT["fcl40_usd"]
        boxes = 1 if cbm <= 28 or cbm <= 67 else math.ceil(cbm / 67)
        fcl = usd(fcl_box[c]) * boxes + FREIGHT["fixed_fcl_eur"][c] + FREIGHT["inland_fcl_eur"][c]
        if lcl <= fcl:
            return lcl, "LCL"
        return fcl, "FCL 20ft" if cbm <= 28 else "FCL 40ft"
    if route == "ж/д":
        lcl = usd(FREIGHT["rail_lcl_usd_cbm"][c]) * cbm + FREIGHT["fixed_lcl_eur"][c] + FREIGHT["inland_lcl_eur"][c]
        fcl = usd(FREIGHT["rail_fcl40_usd"][c]) * max(1, math.ceil(cbm / 67)) + FREIGHT["fixed_fcl_eur"][c] + FREIGHT["inland_fcl_eur"][c]
        return (lcl, "LCL") if lcl <= fcl else (fcl, "FCL 40ft")
    if route == "авиа":
        kg = max(UNIT_KG, UNIT_CBM * 1e6 / 6000) * n
        return usd(FREIGHT["air_usd_kg"][c]) * kg + FREIGHT["fixed_air_eur"][c], "авиа"
    if route == "экспресс":
        kg = max(UNIT_KG, UNIT_CBM * 1e6 / 5000) * n
        return usd(FREIGHT["express_usd_kg"][c]) * kg, "экспресс"
    raise ValueError(route)


def landed(source, n, c, route="море", vat_recoverable=False):
    """Стоимость одного аппарата «от двери до двери» (EUR). Строки — слагаемые."""
    ro = RO_BASE_EUR
    L = {}
    if source == "A":
        L["цена (FOB/EXW)"] = usd(A["price_usd"][c])
        L["упаковка"] = A["packing_eur"][c]
        fr, mode = freight_a(route, n, c)
        L["фрахт"] = fr / n
        cif_wo_ins = L["цена (FOB/EXW)"] + L["упаковка"] + L["фрахт"]
        L["страховка"] = INSURANCE_RATE[c] * 1.1 * cif_wo_ins
        cif = cif_wo_ins + L["страховка"]
        L["пошлина"] = A["duty"][c] * cif
        L["брокер"] = BROKER_EUR[c] / n
        L["внутренняя доставка"] = INLAND_EUR[c]
        L["установка"] = INSTALL_EUR[c]
        vat_base = cif + L["пошлина"] + L["брокер"] + L["внутренняя доставка"] + L["установка"]
        L["НДС 20%"] = 0.0 if vat_recoverable else VAT * vat_base
        L["резерв на гарантию"] = A["warranty_pct"][c] * L["цена (FOB/EXW)"]
        L["_режим"] = mode
    elif source == "B":
        L["цена (FOB/EXW)"] = B["k"][c] * ro
        L["упаковка"] = 0.0
        L["фрахт"] = 0.0
        L["страховка"] = 0.0
        L["пошлина"] = 0.0
        L["брокер"] = 0.0
        L["внутренняя доставка"] = INLAND_EUR[c]
        L["установка"] = INSTALL_EUR[c]
        vat_base = L["цена (FOB/EXW)"] + L["внутренняя доставка"] + L["установка"]
        L["НДС 20%"] = 0.0 if vat_recoverable else VAT * vat_base
        L["резерв на гарантию"] = B["warranty_pct"][c] * L["цена (FOB/EXW)"]
        L["_режим"] = "местная поставка"
    elif source == "D":
        L["цена (FOB/EXW)"] = D["k"][c] * ro
        L["упаковка"] = D["packing_eur"][c]
        fr = D["ftl_eur"][c] if n >= 10 else D["pallet_eur"][c] * n
        L["фрахт"] = fr / n
        cif_wo_ins = L["цена (FOB/EXW)"] + L["упаковка"] + L["фрахт"]
        L["страховка"] = INSURANCE_RATE[c] * 1.1 * cif_wo_ins
        cif = cif_wo_ins + L["страховка"]
        L["пошлина"] = 0.0  # происхождение ЕС + EUR.1 [web] biznis.rs (источник выше)
        L["брокер"] = BROKER_EUR[c] / n
        L["внутренняя доставка"] = INLAND_EUR[c]
        L["установка"] = INSTALL_EUR[c]
        vat_base = cif + L["брокер"] + L["внутренняя доставка"] + L["установка"]
        L["НДС 20%"] = 0.0 if vat_recoverable else VAT * vat_base
        L["резерв на гарантию"] = D["warranty_pct"][c] * L["цена (FOB/EXW)"]
        L["_режим"] = "паллеты" if n < 10 else "FTL"
    else:
        raise ValueError(source)
    L["ИТОГО"] = sum(v for k, v in L.items() if not k.startswith("_") and k != "ИТОГО")
    return L


LINES = ["цена (FOB/EXW)", "упаковка", "фрахт", "страховка", "пошлина", "НДС 20%", "брокер",
         "внутренняя доставка", "установка", "резерв на гарантию", "ИТОГО"]


def modules_total(c):
    return sum(v[c] for v in MODULES_EUR.values())


def landed_extra_over_fob(n, c=1):
    """Сколько добавляет доставка к FOB-цене 915 EUR, заложенной в calculator (источник A, море)."""
    return landed("A", n, c)["ИТОГО"] - RO_BASE_EUR


# ---------------------------------------------------------------------------
# 4. Финансовая модель точки
# ---------------------------------------------------------------------------
def pilot_baseline():
    hardware = 0.0
    fixed = {}
    for block in calc.BLOCKS:
        cur = calc.BLOCK_CURRENCY.get(block, "EUR")
        for row in calc.parse_block(block):
            kind, *rest = calc.SCOPE[row["item"]]
            total = row["total"].strip() if row["total"] else ""
            if total.endswith("%") or not total:
                continue
            amt = float(total) * (EUR_TO_RSD if cur == "EUR" else USD_TO_RSD if cur == "USD" else 1.0)
            if kind == "hardware":
                hardware += amt
            elif kind == "fixed":
                fixed[row["item"]] = amt / rest[0]
    return hardware, fixed


HARDWARE_RSD, FIXED_ROWS = pilot_baseline()
RENT_BASE_RSD = FIXED_ROWS["5.1"]
FIXED_OTHER_RSD = sum(v for k, v in FIXED_ROWS.items() if k != "5.1")
assert abs(sum(g[1] for g in ASSET_GROUPS) * EUR_TO_RSD - HARDWARE_RSD) < 1.0, "группы активов не сходятся со сметой"


def point(lpd, price, rent_x=1.0, theft=0.05, config="standard", capex_adjust_eur=0.0, p=None):
    """Месячный P&L одной точки (RSD). capex_adjust_eur — добавка доставки к CAPEX."""
    p = p or PARAMS
    liters = lpd * 30
    revenue = price * liters
    water_l = p["water_tariff_rsd_m3"] / 1000 * p["reject_multiplier"]
    water = water_l * liters
    fee = revenue * p["payment_fee"]
    tax = revenue * p["tax_rate"]
    rent = p["rent_eur_base"] * rent_x * EUR_TO_RSD
    fixed_cash = rent + FIXED_OTHER_RSD + p["lab_rsd_month"]
    extra = REINFORCED_EXTRA_PCT * RO_BASE_EUR if config == "reinforced" else 0.0
    theft_p = theft * (REINFORCED_THEFT_FACTOR if config == "reinforced" else 1.0)
    theft_loss = theft_p * THEFT_LOSS_EUR * EUR_TO_RSD / 12
    insurance = p["insurance_eur_year"] * EUR_TO_RSD / 12
    dep = 0.0
    for name, eur, life in ASSET_GROUPS:
        if life:
            add = extra if "Корпус" in name else capex_adjust_eur if "RO-блок" in name else 0.0
            dep += (eur + add) * EUR_TO_RSD / (life * 12)
    capex = HARDWARE_RSD + (extra + capex_adjust_eur) * EUR_TO_RSD
    contribution = revenue - water - fee - tax
    net_cash = contribution - fixed_cash - theft_loss - insurance
    net_econ = net_cash - dep
    unit_contrib = price * (1 - p["payment_fee"] - p["tax_rate"]) - water_l
    be_cash = (fixed_cash + theft_loss + insurance) / unit_contrib / 30 if unit_contrib > 0 else float("inf")
    be_econ = (fixed_cash + theft_loss + insurance + dep) / unit_contrib / 30 if unit_contrib > 0 else float("inf")
    payback = capex / net_cash if net_cash > 0 else None
    return dict(lpd=lpd, price=price, revenue=revenue, water=water, fee=fee, tax=tax, rent=rent,
                fixed_other=FIXED_OTHER_RSD + p["lab_rsd_month"], theft=theft_loss, insurance=insurance,
                dep=dep, contribution=contribution, net_cash=net_cash, net_econ=net_econ,
                be_cash=be_cash, be_econ=be_econ, payback=payback, capex=capex, unit_contrib=unit_contrib)


def months(v):
    return "не окупается" if v is None else f"{v:.0f}"


def be_fmt(v):
    return "нет" if v == float("inf") else f"{v:.0f}"


# ---------------------------------------------------------------------------
# 5. Вывод
# ---------------------------------------------------------------------------
def write(name, lines):
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, name)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    return path


def financial_model():
    extra1 = landed_extra_over_fob(1)
    L = []
    L.append("# Финансовая модель: сценарии, чувствительность, 1/5/20 точек\n")
    L.append("Сгенерировано `pipeline/economics.py` (запуск из корня: `python3 pipeline/economics.py`). Модель использует смету и классификацию `pipeline/calculator.py` (`SCOPE`) и не меняет её. Курсы: 1 EUR = 117 RSD, 1 USD = 107 RSD (`pipeline/fx.py`). Метки: [repo], [web], [заполнитель] — значение подставлено без найденного источника, заменить данными пилота или котировкой; «ожидает дорожку X» — вход зависит от параллельной дорожки.\n")
    L.append("## 1. Параметры\n")
    L.append("| Параметр | Значение | Источник |")
    L.append("|---|---|---|")
    L.append(f"| Цена | {PARAMS['price_per_l']:.0f} RSD/л (50 RSD за 5 л) | [repo] решение 0004 |")
    L.append(f"| Вода | {PARAMS['water_tariff_rsd_m3']} RSD/м³ × {PARAMS['reject_multiplier']} (сброс RO) = {PARAMS['water_tariff_rsd_m3']/1000*PARAMS['reject_multiplier']:.2f} RSD/л | [repo] факт 0003, допущение `calculator.py` |")
    L.append(f"| Комиссия платежей | {PARAMS['payment_fee']:.1%} выручки | [repo] `calculator.py`, FINANCE 3.5 (диапазон 1,5–3%) |")
    L.append(f"| Налог | {PARAMS['tax_rate']:.0%} выручки | [repo] `calculator.py` |")
    L.append(f"| Аренда (база) | {PARAMS['rent_eur_base']:.0f} EUR/мес = {fmt(RENT_BASE_RSD)} RSD | [repo] бриф §3.1 (пример, не договор) |")
    L.append(f"| Прочие постоянные (обслуживание, фильтры, GPS, мониторинг, сервис) | {fmt(FIXED_OTHER_RSD)} RSD/мес | [repo] `pilot-scenarios.md` §3 |")
    L.append(f"| Оборудование и установка пилота | {fmt(HARDWARE_RSD)} RSD ({fmt(HARDWARE_RSD/EUR_TO_RSD)} EUR), без фрахта, пошлины, НДС | [repo] `pilot-scenarios.md` §1 |")
    L.append(f"| Добавка доставки к CAPEX (источник A, море, середина, 1 аппарат) | {fmt(extra1)} EUR | расчёт `ready_made_options.md` |")
    L.append(f"| Страхование | {PARAMS['insurance_eur_year']} EUR/год | [web] ориентир Хорватия (Wiener), не Сербия |")
    L.append(f"| Ущерб от одного события кражи/вандализма | {THEFT_LOSS_EUR:.0f} EUR | [заполнитель] |")
    L.append(f"| Анализы воды | {PARAMS['lab_rsd_month']:.0f} RSD/мес (не включены) | цена не найдена; ожидает дорожки sampling, certification |")
    L.append("")
    L.append("### Амортизация (линейная, по группам)\n")
    L.append("| Группа | EUR | Срок, лет | RSD/мес |")
    L.append("|---|---|---|---|")
    tot = 0.0
    for name, eur, life in ASSET_GROUPS:
        m = eur * EUR_TO_RSD / (life * 12) if life else 0.0
        tot += m
        L.append(f"| {name} | {fmt(eur)} | {life if life else '—'} | {fmt(m)} |")
    L.append(f"| **Итого** | **{fmt(sum(g[1] for g in ASSET_GROUPS))}** | | **{fmt(tot)}** |")
    L.append("")
    L.append("Сроки службы — [заполнитель], согласовать с бухгалтером; налоговая амортизация Сербии: пять групп 2,5/10/15/20/30%, не перечисленное в II–V попадает в III группу (15%) [web] KPMG (ссылка выше). Группа для оборудования водоматов **не найдена**; признаваемый расход ограничен бухгалтерской амортизацией.\n")

    L.append("## 2. Сценарии одной точки (пилот, конфигурация standard)\n")
    L.append(f"Добавка доставки к CAPEX учтена: +{fmt(extra1)} EUR к RO-блоку.\n")
    L.append("| Сценарий | л/день | Выручка | Вода | Комиссия | Налог | Аренда | Прочие пост. | Кража (ож.) | Страх. | Прибыль (денежная) | Амортизация | Прибыль после аморт. | Безубыточность л/день (денежная / с аморт.) | Окупаемость, мес |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for name, s in SCENARIOS.items():
        r = point(s["lpd"], s["price"], s["rent_x"], s["theft"], "standard", extra1)
        L.append(f"| {name} | {r['lpd']} | {fmt(r['revenue'])} | {fmt(r['water'])} | {fmt(r['fee'])} | {fmt(r['tax'])} | {fmt(r['rent'])} | {fmt(r['fixed_other'])} | {fmt(r['theft'])} | {fmt(r['insurance'])} | {fmt(r['net_cash'])} | {fmt(r['dep'])} | {fmt(r['net_econ'])} | {be_fmt(r['be_cash'])} / {be_fmt(r['be_econ'])} | {months(r['payback'])} |")
    L.append("")
    L.append("Сверка с `calculator.py`: без добавки доставки, амортизации, кражи и страхования точка 50/80 л/день даёт −24 724/−17 328 RSD/мес, безубыточность ≈150 л/день; здесь добавлены ожидаемые потери от кражи и страхование (денежная безубыточность выше), а также амортизация и доставка (безубыточность «с амортизацией» заметно выше).\n")
    r0 = point(80, 10.0, 1.0, 0.0, "standard", 0.0, dict(PARAMS, insurance_eur_year=0.0))
    L.append(f"Проверка: при нулевых кражах, страховке и доставке модель даёт {fmt(r0['net_cash'])} RSD/мес при 80 л/день и безубыточность {be_fmt(r0['be_cash'])} л/день — совпадает с `pilot-scenarios.md` (−17 328 и ≈150).\n")

    L.append("## 3. Типы локаций\n")
    L.append("Параметры типов — [заполнитель], ожидает дорожку hardware (`docs/hardware/location-types.md`, `configurations.md`); пересчитать после слияния.\n")
    L.append("| Тип | Аренда, EUR/мес | Конфигурация | л/день | Риск кражи/год | Прибыль денежная, RSD/мес | После аморт. | Безубыточность л/день | Окупаемость, мес |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for name, t in LOCATION_TYPES.items():
        r = point(t["lpd"], 10.0, t["rent_x"], t["theft"], t["config"], extra1)
        L.append(f"| {name} | {PARAMS['rent_eur_base']*t['rent_x']:.0f} | {t['config']} | {t['lpd']} | {t['theft']:.0%} | {fmt(r['net_cash'])} | {fmt(r['net_econ'])} | {be_fmt(r['be_cash'])} / {be_fmt(r['be_econ'])} | {months(r['payback'])} |")
    L.append("")

    L.append("## 4. Чувствительность (базовый сценарий: 80 л/день, 10 RSD/л, аренда 150 EUR, риск кражи 5%/год)\n")
    base = point(80, 10.0, 1.0, 0.05, "standard", extra1)
    L.append(f"Базовая прибыль после амортизации: {fmt(base['net_econ'])} RSD/мес; денежная: {fmt(base['net_cash'])}.\n")

    def sens(title, header, rows):
        L.append(f"**{title}**\n")
        L.append(f"| {header} | Прибыль денежная | После аморт. | Безубыточность л/день (с аморт.) |")
        L.append("|---|---|---|---|")
        for label, r in rows:
            L.append(f"| {label} | {fmt(r['net_cash'])} | {fmt(r['net_econ'])} | {be_fmt(r['be_econ'])} |")
        L.append("")

    sens("Аренда", "Аренда, EUR/мес", [(f"{150*x:.0f}", point(80, 10.0, x, 0.05, "standard", extra1)) for x in (0.0, 0.5, 1.0, 2.0, 3.0)])
    sens("Цена за литр (объём неизменен; эластичность — в `pricing-scenarios.md`)", "Цена, RSD/л", [(f"{pr}", point(80, pr, 1.0, 0.05, "standard", extra1)) for pr in (5, 8, 10, 12, 15)])
    sens("Объём", "л/день", [(f"{v}", point(v, 10.0, 1.0, 0.05, "standard", extra1)) for v in (30, 50, 80, 120, 150, 200, 300)])
    sens("Риск кражи (вероятность события в год; ущерб 1500 EUR)", "Вероятность/год", [(f"{t:.0%}", point(80, 10.0, 1.0, t, "standard", extra1)) for t in (0.0, 0.05, 0.10, 0.20, 0.40)])
    sens("Коэффициент сброса RO (литров воды на проданный литр)", "Коэффициент", [(f"{k}", point(80, 10.0, 1.0, 0.05, "standard", extra1, dict(PARAMS, reject_multiplier=k))) for k in (2, 3, 4, 5)])
    sens("Комиссия платежей", "Комиссия", [(f"{c:.1%}", point(80, 10.0, 1.0, 0.05, "standard", extra1, dict(PARAMS, payment_fee=c))) for c in (0.015, 0.02, 0.03)])
    uc = base["unit_contrib"]
    L.append(f"**Цена ошибки в постоянных расходах:** каждые +1 000 RSD/мес постоянных расходов (например, анализы воды) поднимают безубыточность на {1000/uc/30:.1f} л/день (вклад {uc:.2f} RSD/л).\n")

    L.append("## 5. Сеть: 1, 5 и 20 точек\n")
    L.append("Точка — базовый сценарий (80 л/день, 10 RSD/л, аренда 150 EUR, риск 5%). Общие (не связанные с размещением) затраты — отдельными строками; значения — [заполнитель], источников нет, уточнить у бухгалтера, юриста, подрядчика. CAPEX на точку включает доставку источника A (море, середина) для партии N.\n")
    L.append("| Статья, RSD/мес | 1 | 5 | 20 |")
    L.append("|---|---|---|---|")
    rows = {}
    for n in (1, 5, 20):
        e = landed_extra_over_fob(n)
        r = point(80, 10.0, 1.0, 0.05, "standard", e)
        rows[n] = (r, e)
    def line(label, fn):
        L.append(f"| {label} | " + " | ".join(fmt(fn(n)) for n in (1, 5, 20)) + " |")
    line("Выручка сети", lambda n: n * rows[n][0]["revenue"])
    line("Переменные (вода, комиссия, налог)", lambda n: n * (rows[n][0]["water"] + rows[n][0]["fee"] + rows[n][0]["tax"]))
    line("Размещение: аренда", lambda n: n * rows[n][0]["rent"])
    line("Постоянные на точке (обслуживание, фильтры, GPS, мониторинг)", lambda n: n * rows[n][0]["fixed_other"])
    line("Кража (ожидаемая) + страхование", lambda n: n * (rows[n][0]["theft"] + rows[n][0]["insurance"]))
    shared_tot = {}
    for sname, vals in SHARED_COSTS_EUR_MONTH.items():
        line(f"Общие: {sname}", lambda n, vals=vals: vals[n] * EUR_TO_RSD)
    for n in (1, 5, 20):
        shared_tot[n] = sum(v[n] for v in SHARED_COSTS_EUR_MONTH.values()) * EUR_TO_RSD
    line("**Общие затраты, всего**", lambda n: shared_tot[n])
    line("**Прибыль сети (денежная)**", lambda n: n * rows[n][0]["net_cash"] - shared_tot[n])
    line("Амортизация", lambda n: n * rows[n][0]["dep"])
    line("**Прибыль сети после амортизации**", lambda n: n * rows[n][0]["net_econ"] - shared_tot[n])
    line("CAPEX сети (оборудование + доставка)", lambda n: n * rows[n][0]["capex"])
    L.append("")
    L.append("| Показатель | 1 | 5 | 20 |")
    L.append("|---|---|---|---|")
    be = {}
    for n in (1, 5, 20):
        r = rows[n][0]
        fixed_all = n * (r["rent"] + r["fixed_other"] + r["theft"] + r["insurance"] + r["dep"]) + shared_tot[n]
        be[n] = fixed_all / (r["unit_contrib"] * 30 * n)
    L.append("| Безубыточность на точку, л/день (с амортизацией и общими) | " + " | ".join(f"{be[n]:.0f}" for n in (1, 5, 20)) + " |")
    L.append("| Общие затраты на точку, RSD/мес | " + " | ".join(fmt(shared_tot[n] / n) for n in (1, 5, 20)) + " |")
    pb = []
    for n in (1, 5, 20):
        net = n * rows[n][0]["net_cash"] - shared_tot[n]
        pb.append(months(n * rows[n][0]["capex"] / net if net > 0 else None))
    L.append("| Окупаемость CAPEX, мес | " + " | ".join(pb) + " |")
    L.append("")
    L.append("Вывод: при 80 л/день сеть из 5 и 20 точек остаётся убыточной; масштабирование имеет смысл, только если пилот покажет объём заметно выше 150 л/день (решение 0011, правило `no-scale-out-before-pilot-gate`).\n")
    L.append("## 6. Источники и ограничения\n")
    L.append("- Смета и классификация: `pipeline/calculator.py`, `docs/cost-estimates/blocks/*.md` [repo].")
    L.append("- Доставка и закупка: `docs/economics/ready-made-options-landed-cost.md` (там же ссылки [web]).")
    L.append("- Не учтено: анализы воды, фискализация (стоимость не найдена), стоимость капитала, налог на прибыль сверх плоских 10% выручки, НДС с выручки (см. `pricing.md`).")
    L.append("- Конфигурации, локации, сертификация, пробы: ожидает дорожки hardware, certification, sampling.")
    return write("financial-model.md", L), rows, be, shared_tot


def pricing_table():
    extra1 = landed_extra_over_fob(1)
    L = []
    L.append("# Сценарии цены (генерируется `pipeline/economics.py`)\n")
    L.append("База: 80 л/день при 10 RSD/л (50 RSD за 5 л). Эластичность спроса e — [заполнитель]: данных по Сербии нет, значение определяет пилот. Объём V(p) = 80 × (p/10)^(−e). Прибыль — после амортизации, аренда 150 EUR, риск кражи 5%/год.\n")
    for e in (0.5, 1.0, 1.5):
        L.append(f"**Эластичность e = {e}**\n")
        L.append("| Цена RSD/л | за 5 л | л/день | Выручка | Прибыль денежная | После аморт. | Безубыточность л/день |")
        L.append("|---|---|---|---|---|---|---|")
        for pr in (5, 8, 10, 12, 15):
            v = 80 * (pr / 10) ** (-e)
            r = point(v, float(pr), 1.0, 0.05, "standard", extra1)
            L.append(f"| {pr} | {pr*5} | {v:.0f} | {fmt(r['revenue'])} | {fmt(r['net_cash'])} | {fmt(r['net_econ'])} | {be_fmt(r['be_econ'])} |")
        L.append("")
    L.append("**Если цена включает НДС 20% (плательщик НДС)** — чистая цена p/1,2; при e = 1:\n")
    L.append("| Цена с НДС RSD/л | Чистая цена | л/день | Прибыль после аморт. | Безубыточность л/день |")
    L.append("|---|---|---|---|---|")
    for pr in (8, 10, 12, 15):
        v = 80 * (pr / 10) ** (-1.0)
        r = point(v, pr / 1.2, 1.0, 0.05, "standard", extra1)
        L.append(f"| {pr} | {pr/1.2:.2f} | {v:.0f} | {fmt(r['net_econ'])} | {be_fmt(r['be_econ'])} |")
    L.append("")
    L.append("**Цена, при которой точка безубыточна при заданном объёме** (после амортизации, без НДС в цене):\n")
    L.append("| л/день | Минимальная цена, RSD/л |")
    L.append("|---|---|")
    for v in (50, 80, 120, 150, 200):
        lo, hi = 1.0, 100.0
        for _ in range(60):
            mid = (lo + hi) / 2
            if point(v, mid, 1.0, 0.05, "standard", extra1)["net_econ"] >= 0:
                hi = mid
            else:
                lo = mid
        L.append(f"| {v} | {hi:.1f} |")
    L.append("")
    return write("pricing-scenarios.md", L)


def ready_made():
    L = []
    L.append("# Покупка готового аппарата: стоимость «от двери до двери» (Door-to-door)\n")
    L.append("Сгенерировано `pipeline/economics.py`. Это **оценка по диапазонам**, а не котировка: RFQ (`docs/project/supplier-rfq.md`) не отправлен. Пустые ячейки «Котировка» в §6 заполняются реальными предложениями. Курсы: 1 EUR = 117 RSD, 1 USD = 107 RSD. Метки: [web], [repo], [заполнитель] (подставлено без найденного источника — заменить), «не найдено» — данных нет, кого спросить указано в §7.\n")
    L.append("## 1. Допущения и источники\n")
    L.append("| Позиция | Низ / середина / верх | Источник |")
    L.append("|---|---|---|")
    L.append(f"| A: цена аппарата класса RO-300A, FOB, USD | {' / '.join(map(str, A['price_usd']))} | [web] объявления 590–2000 USD (`pilot-launch-guide.md` §2.1), 1000 USD [repo] `initial-technical-spec.md` §9.3 |")
    L.append(f"| Упаковка экспортная, EUR/ед. | {' / '.join(map(str, A['packing_eur']))} | [заполнитель]; уточнить у поставщика, входит ли в цену |")
    L.append(f"| Кубатура / вес упакованного аппарата | {UNIT_CBM} м³ / {UNIT_KG:.0f} кг | [заполнитель]; запросить у поставщика |")
    L.append(f"| Море LCL, USD/м³ | {' / '.join(map(str, FREIGHT['lcl_usd_cbm']))} (160–290) | [web] https://goodhopefreight.com/serbia.html (без даты; порт Копер/Бар, 40–55 сут) |")
    L.append(f"| Море FCL 20ft / 40ft, USD | {FREIGHT['fcl20_usd'][0]}–{FREIGHT['fcl20_usd'][2]} / {FREIGHT['fcl40_usd'][0]}–{FREIGHT['fcl40_usd'][2]} | [web] там же (35–50 сут). К Греции (Пирей/Салоники) 40HQ: 2 850 (дек. 2025) – 6 550 (июнь 2026) USD, https://goodhopefreight.com/greece/2026-freight.html, без наземной части в Сербию |")
    L.append(f"| Ж/д Китай→Белград, 40ft, USD | 8 850–9 250 (июнь–август 2026, без пункта назначения, 18–25 сут) | [web] https://goodhopefreight.com/serbia/2026-freight.html |")
    L.append(f"| Ж/д LCL, USD/м³ | 150–400 (без даты) | [web] https://www.sino-shipping.com/zh/rail-freight-from-china/costs/average-rail-freight-cost-per-container-china-to-europe/ |")
    L.append(f"| Авиа, USD/кг | 5–9 (аэропорт–аэропорт, 5–10 сут; объёмный вес /6000) | [web] https://goodhopefreight.com/serbia.html |")
    L.append(f"| Экспресс, USD/кг | 10–18 (дверь–дверь, 3–7 сут; объёмный вес /5000) | [web] там же |")
    L.append(f"| Сборы по концам, EUR за отправку (LCL / FCL / авиа) | {FREIGHT['fixed_lcl_eur'][0]}–{FREIGHT['fixed_lcl_eur'][2]} / {FREIGHT['fixed_fcl_eur'][0]}–{FREIGHT['fixed_fcl_eur'][2]} / {FREIGHT['fixed_air_eur'][0]}–{FREIGHT['fixed_air_eur'][2]} | не найдено, [заполнитель]; спросить форвардера |")
    L.append(f"| Автовывоз Копер/Бар→Белград (631 км), EUR за отправку (LCL / FCL) | {FREIGHT['inland_lcl_eur'][0]}–{FREIGHT['inland_lcl_eur'][2]} / {FREIGHT['inland_fcl_eur'][0]}–{FREIGHT['inland_fcl_eur'][2]} | ставка не найдена, [заполнитель]; расстояние [web] rome2rio |")
    L.append(f"| Страховка | 0,3 / 0,4 / 0,5% от (CIF + 10%) | [web] https://gofreight.com/glossary/cargo-insurance |")
    L.append(f"| Пошлина A | 0 / 5 / 10% от CIF | 10% — упрощённая процедура [web] biznis.rs; 0% возможна по FTA Китай–Сербия с 01.07.2024 [web] srbija.gov.rs; ставка по подсубпозиции 8421 21 не найдена, спросить брокера; 5% — середина диапазона для расчёта |")
    L.append(f"| Пошлина D | 0% | [web] товары ЕС с EUR.1 или декларацией на счёте — без пошлины (biznis.rs); НДС остаётся |")
    L.append(f"| НДС | 20% от (CIF + пошлина) и от услуг | [web] biznis.rs; возврат только у плательщика НДС (порог обязательной регистрации 8 000 000 RSD оборота за 12 мес, [web] https://zuniclaw.com/pdv-registracija-u-srbiji), добровольная регистрация — не найдено, спросить бухгалтера |")
    L.append(f"| Брокер, EUR за отправку | {' / '.join(map(str, BROKER_EUR))} | низ: DHL Сербия 5 265 RSD за импортное оформление [web] https://mydhl.express.dhl/rs/sr/ship/customs-services.html (уточнить, для юрлиц ли цена); середина и верх — [заполнитель] |")
    L.append(f"| Внутренняя доставка до площадки / установка, EUR/ед. | {' / '.join(map(str, INLAND_EUR))} / {' / '.join(map(str, INSTALL_EUR))} | [заполнитель]; в CAPEX пилота отдельно уже есть учёт (200 EUR) и интеграция [repo] |")
    L.append(f"| B: цена = k × 915 EUR (без НДС, поставка до Белграда включена) | k = {' / '.join(map(str, B['k']))} | допущение по правилу решения 0012 (B/D допустимы до ≈2× от A); котировки нет |")
    L.append(f"| D: цена EXW = k × 915 EUR | k = {' / '.join(map(str, D['k']))} | допущение; Ecosoft Aquabox и др.: «цена по запросу» [web] https://www.ecosoft.com/en-gb/product/424 |")
    L.append(f"| D: паллет, EUR / FTL (≥10 ед.), EUR | {D['pallet_eur'][0]}–{D['pallet_eur'][2]} / {D['ftl_eur'][0]}–{D['ftl_eur'][2]} | не найдено, [заполнитель]; перевозчики: M&M (линия Штутгарт–Белград), DHL Freight |")
    L.append(f"| Резерв на гарантию, % от цены (A / B / D) | 3–8 / 0–4 / 1–4 | [заполнитель]; гарантия 2 года на насос и мембрану — обычная практика по [web] https://smartbuy.alibaba.com/buyingguides/water-atm-vending-machine |")
    L.append("")

    def block(title, source, n, cases=(0, 1, 2), route="море", vat_rec=False):
        res = [landed(source, n, c, route, vat_rec) for c in cases]
        out = [f"**{title}**\n", "| Статья, EUR на аппарат | " + " | ".join(CASES[c] for c in cases) + " |", "|---|" + "---|" * len(cases)]
        for ln in LINES:
            out.append(f"| {'**' + ln + '**' if ln == 'ИТОГО' else ln} | " + " | ".join(fmt(r[ln]) for r in res) + " |")
        out.append("| ИТОГО, RSD | " + " | ".join(fmt(rsd(r['ИТОГО'])) for r in res) + " |")
        return out, res

    L.append("## 2. Door-to-door по источнику (EUR на один аппарат, НДС не возвращается)\n")
    L.append("Только аппарат (класс RO-300A, без общего блока модулей из §5). Режим перевозки A — море (LCL/FCL подбирается по минимуму стоимости).\n")
    summary = {}
    for src, label in (("A", "A. Китайский производитель"), ("B", "B. Местный дистрибьютор"), ("D", "D. Европейский поставщик")):
        for n in (1, 5, 20):
            out, res = block(f"{label}, {n} шт. (режим: {res0(src, n)})", src, n)
            L += out
            L.append("")
            summary[(src, n)] = res
    L.append("## 3. Сводная таблица «по источнику» (Door-to-door, EUR на аппарат, середина; в скобках диапазон низ–верх)\n")
    L.append("| Источник | 1 шт. | 5 шт. | 20 шт. | Отношение к A (1 шт., середина) |")
    L.append("|---|---|---|---|---|")
    a1 = summary[("A", 1)][1]["ИТОГО"]
    for src, label in (("A", "A Китай"), ("B", "B местный дистрибьютор"), ("D", "D Европа")):
        cells = []
        for n in (1, 5, 20):
            r = summary[(src, n)]
            cells.append(f"{fmt(r[1]['ИТОГО'])} ({fmt(r[0]['ИТОГО'])}–{fmt(r[2]['ИТОГО'])})")
        L.append(f"| {label} | " + " | ".join(cells) + f" | ×{summary[(src,1)][1]['ИТОГО']/a1:.2f} |")
    L.append("")
    L.append("То же в RSD (середина): " + "; ".join(f"{s} 1 шт. {fmt(rsd(summary[(s,1)][1]['ИТОГО']))}" for s in ("A", "B", "D")) + ".\n")
    ratioB = summary[("B", 1)][1]["ИТОГО"] / a1
    ratioD = summary[("D", 1)][1]["ИТОГО"] / a1
    L.append(f"Проверка правила решения 0012 (B или D, если цена не выше ≈2× от A): по door-to-door B = ×{ratioB:.2f}, D = ×{ratioD:.2f} от A (середина, 1 шт.). Правило сформулировано для цен-котировок (FOB против местной цены). По полной стоимости при одном аппарате накладные расходы импорта (фрахт, сборы по концам, брокер, пошлина, НДС) составляют большую часть цены A, поэтому разрыв между A и B/D заметно меньше «двойной» разницы цен; но значительная часть накладных — [заполнитель], вывод предварительный. Пересчитать по реальным котировкам.\n")

    L.append("## 4. Режимы перевозки для A (EUR на аппарат, середина)\n")
    L.append("| Режим | Транзит, суток | 1 шт. | 5 шт. | 20 шт. |")
    L.append("|---|---|---|---|---|")
    for route, tr in (("море", TRANSIT_DAYS["море (LCL)"] + " (LCL) / " + TRANSIT_DAYS["море (FCL)"] + " (FCL)"), ("ж/д", TRANSIT_DAYS["ж/д"]), ("авиа", TRANSIT_DAYS["авиа"]), ("экспресс", TRANSIT_DAYS["экспресс"])):
        cells = [fmt(landed("A", n, 1, route)["ИТОГО"]) for n in (1, 5, 20)]
        L.append(f"| {route} | {tr} | " + " | ".join(cells) + " |")
    L.append("")
    L.append("Выводы по режиму: для одного аппарата различия моря, ж/д и авиа сопоставимы с погрешностью допущений (сотни EUR), экспресс заметно дороже; для 20 аппаратов выигрывает море (доля фрахта на аппарат падает). Сроки — [web] те же источники; производство и документы добавляют ещё 5–10 недель (§8).\n")
    L.append("### НДС возвращается (плательщик НДС), источник A, море, середина\n")
    L.append("| 1 шт. | 5 шт. | 20 шт. |")
    L.append("|---|---|---|")
    L.append("| " + " | ".join(fmt(landed("A", n, 1, "море", True)["ИТОГО"]) for n in (1, 5, 20)) + " |")
    L.append("")

    L.append("## 5. Общий блок модулей (одинаков для A, B, D; не входит в сравнение источников)\n")
    L.append("| Модуль | Низ / середина / верх, EUR | Источник |")
    L.append("|---|---|---|")
    for k, v in MODULES_EUR.items():
        L.append(f"| {k} | {v[0]} / {v[1]} / {v[2]} | [repo] `initial-technical-spec.md` §9.3, TECH 1.4–1.10, 1.9 |")
    L.append(f"| **Итого (до НДС)** | **{modules_total(0)} / {modules_total(1)} / {modules_total(2)}** | |")
    L.append("")
    L.append("Для справки: платёжный терминал Nayax VPOS Touch — 399 USD (≈365 EUR), от 5 шт. 314 USD, от 15 шт. 289 USD, плюс 9,99 USD/мес за облачную услугу [web] https://shop.nayax.com/vpos-touch.html (версия для сотовой сети США; версию для Европы уточнить у Nayax). Фискальное решение (ESIR) в 2026: стоимость и наличие не найдены (факт 0010).\n")

    L.append("## 6. Шаблон для реальных котировок\n")
    L.append("| Источник | Поставщик | Дата | Цена, валюта | Incoterm | Упаковка | Фрахт | Страховка | Пошлина (код, ставка) | Брокер | Срок производства, дн. | Срок доставки, дн. | Гарантия | Комментарий |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for s in ("A (1)", "A (2)", "A (3)", "B", "D"):
        L.append(f"| {s} | | | | | | | | | | | | | |")
    L.append("")
    L.append("Формула: Door-to-door = цена + упаковка + фрахт + страховка + пошлина + НДС 20% + брокер + внутренняя доставка + установка + резерв на гарантию. Страховка = ставка × 1,1 × (цена + упаковка + фрахт). Пошлина = ставка × CIF. НДС = 20% × (CIF + пошлина + услуги в Сербии), в расчёт не входит у плательщика НДС.\n")

    L.append("## 7. Пробелы (не найдено) и кого спросить\n")
    L.append("| Что | Кого спросить |")
    L.append("|---|---|")
    for a, b in (
        ("Цены B и D", "белградский дистрибьютор (импортёр водоматов); Ecosoft и другие европейские поставщики"),
        ("Пошлина по 8421 21 для происхождения Китай и ЕС", "таможенный брокер; Управа царина (Uprava carina)"),
        ("Фиксированные сборы порта/терминала, автовывоз Копер/Бар–Белград", "2–3 форвардера (в т.ч. Pluton Logistics, M&M Serbia)"),
        ("Ставка брокера за декларацию на коммерческий груз", "лицензированные брокеры, форвардер"),
        ("Вес и кубатура упакованного аппарата", "поставщик (в RFQ)"),
        ("Возврат НДС и добровольная регистрация", "бухгалтер, Налоговая администрация"),
        ("Гарантия, сроки производства", "поставщики (в RFQ)"),
    ):
        L.append(f"| {a} | {b} |")
    L.append("")

    L.append("## 8. Срок поставки по этапам, суток (для A, море)\n")
    L.append("| Этап | Низ | Середина | Верх | Источник |")
    L.append("|---|---|---|---|---|")
    tot = [0, 0, 0]
    for k, v in STAGES_DAYS.items():
        L.append(f"| {k} | {v[0]} | {v[1]} | {v[2]} | [заполнитель] |")
        for i in range(3):
            tot[i] += v[i]
    sea = (35, 42, 55)
    L.append(f"| Транзит море (FCL 35–50, LCL 40–55) | {sea[0]} | {sea[1]} | {sea[2]} | [web] goodhopefreight.com |")
    for i in range(3):
        tot[i] += sea[i]
    L.append(f"| **Всего** | **{tot[0]}** (~{tot[0]/7:.0f} нед.) | **{tot[1]}** (~{tot[1]/7:.0f} нед.) | **{tot[2]}** (~{tot[2]/7:.0f} нед.) | |")
    L.append("")
    air = (5, 7.5, 10)
    t2 = [sum(v[i] for v in STAGES_DAYS.values()) + air[i] for i in range(3)]
    L.append(f"При авиа: {t2[0]:.0f} / {t2[1]:.0f} / {t2[2]:.0f} суток. Ж/д (18–25 сут): ≈{sum(v[0] for v in STAGES_DAYS.values())+18} / {sum(v[1] for v in STAGES_DAYS.values())+21} / {sum(v[2] for v in STAGES_DAYS.values())+25}. Для B и D сроки не найдены (спросить поставщиков); для D автоперевозка из ЕС — несколько суток [заполнитель].\n")

    L.append("## 9. Собираем или покупаем: бюджет деталей, при котором сборка (вариант C) равна покупке A\n")
    L.append("Сборка из компонентов добавляет работу (16 ч интеграции по 25 EUR/ч = 400 EUR на аппарат, [repo] INTEGRATION 10.14) и разовые затраты на стенд/оснастку ([заполнитель] 1 000 EUR на партию) и закупку деталей отдельно (отдельные фрахт, пошлина, НДС). Ниже — максимальная сумма **деталей франко-Сербия с НДС**, при которой C не дороже A (середина, море, НДС не возвращается).\n")
    L.append("| Партия | Door-to-door A (аппарат), EUR | Работа 400 EUR + оснастка 1000/N, EUR | Бюджет деталей, EUR (с НДС) |")
    L.append("|---|---|---|---|")
    for n in (1, 5, 20):
        a = landed("A", n, 1)["ИТОГО"]
        lab = 400 * (1 + VAT) + 1000 / n * (1 + VAT)
        L.append(f"| {n} | {fmt(a)} | {fmt(lab)} | {fmt(a - lab)} |")
    L.append("")
    L.append("Цены отдельных деталей для 400 GPD найдены лишь частично (см. `in_house_assembly.md`): итоговую сумму деталей нужно сравнить с этим бюджетом после запроса прайсов.\n")
    return write("ready-made-options-landed-cost.md", L), summary


def res0(src, n):
    return landed(src, n, 1)["_режим"]


def main():
    p1, rows, be, shared = financial_model()
    p2 = pricing_table()
    p3, summary = ready_made()
    print("Созданы:", p1, p2, p3, sep="\n  ")
    e1 = landed_extra_over_fob(1)
    print(f"CAPEX пилота (calculator): {HARDWARE_RSD:,.0f} RSD; добавка доставки A/море/середина, 1 шт.: {e1:,.0f} EUR")
    for src in ("A", "B", "D"):
        print(src, {n: round(summary[(src, n)][1]["ИТОГО"]) for n in (1, 5, 20)}, "EUR/ед., середина")
    for name, s in SCENARIOS.items():
        r = point(s["lpd"], s["price"], s["rent_x"], s["theft"], "standard", e1)
        print(f"{name}: {s['lpd']} л/д, прибыль {r['net_cash']:,.0f}, после аморт. {r['net_econ']:,.0f}, безуб. {be_fmt(r['be_cash'])}/{be_fmt(r['be_econ'])} л/д")
    print("Безубыточность сети на точку (с общими):", {n: round(be[n]) for n in be})


if __name__ == "__main__":
    main()
