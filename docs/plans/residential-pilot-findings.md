# Результаты шага 1.1 плана residential-pilot-reconciliation

Устаревшая базовая модель (54 000 RSD/мес, 40 310 чистыми, 7,5 мес, 180 л/день):
- `pipeline/calculator.py`: раньше цена 50 RSD/л и 180 л/день (давало 270 000 RSD/мес, а не 54 000), писал `SMETA_FINAL.md`. Теперь цена 10 RSD/л, сценарии 50 и 80 л/день, вывод в `pilot_scenarios.md`.
- `docs/pipeline/consolidated/SMETA_FINAL.md:14-16,52-68`: 54 000 RSD/мес при 10 RSD/л, 7,5 мес. Правился вручную (пометки [FIXED], раздел о финансировании); не пересобирать из calculator.
- `docs/pipeline/consolidated/summary.md:30-32`: те же цифры. `consolidator.py` его не генерирует (пишет другую сводку); поддерживается вручную, править вручную.
- `docs/technical/PRESENTATION.md:126-142,226`: 180 л/день, 54 000 RSD, 7,5 мес.
- `presentations/business_presentation_single_point.md:61`: «~7,5 месяцев (при 50 л/день)».
- `docs/technical/TECH_SPEC.md:17,254`: 180 л — объём бака; не устарело.

Формулировки «сначала офисы»: `water_vending_brief.md` §3.2–3.3 (добавлено приложение); `water_vending_plan.md`, фаза 3 (3.1, 3.3) и 6.3 (обновлено).

Вердикт по `docs/business_plan/smeta.md`: устаревший (legacy). Внутренне противоречив (в шапке CAPEX ~970 000 и окупаемость 5 мес; в теле CAPEX 483 500 и 2,3 мес; выручка 270 000 RSD/мес из 5 400 л × 50 RSD). Не выведен из пайплайна. Помечен как заменённый.

Корректировка плана: шаг 3.1 правит вручную `summary.md` и `SMETA_FINAL.md`; пересобирается только `pilot_scenarios.md` (через `calculator.py`).
