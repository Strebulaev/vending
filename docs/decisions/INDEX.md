# bootstrap-generated: true
id, title, tags, status
0001-cashless-first,Приоритет — безналичная оплата (телефон/карта); приём наличных необязателен,"payment, hardware",draft
0002-treated-tap-water-product,"Продукт — водопроводная вода, очищенная на месте обратным осмосом, а не бутилированная","water-treatment",draft
0003-residential-single-point-pilot,Проверить одну жилую точку рядом с домом до масштабирования,"locations, pricing",draft
0004-single-price-first,"Сначала проверить одну цену за 5 л, затем дифференцировать по типу точки","pricing",draft
0005-franchise-open-zones-only,Франшиза только в открытых зонах; свой город компания закрывает сама,"franchise",draft
0006-serbia-first-expansion,"Выходить поэтапно, начиная с Сербии, затем Балканы","franchise, legal-tax",draft
0007-hardware-design-principles,"Конструкция аппарата: низкая стоимость, ремонтопригодность, обслуживаемость, наблюдаемость, простая интеграция","hardware, telemetry",draft
0008-signed-tolerances-with-penalties,"Допуски поставщиков подписываются, за нарушения — штрафы","hardware",draft
0009-sourced-estimates,Каждое число сметы имеет открытый источник (URL или файл репозитория); иначе в ячейке пишется not found,"pipeline, finance",draft
0010-english-estimates,Файлы смет пишутся на английском в стандартной 9-колоночной схеме,"documentation, pipeline",draft
0011-pilot-gate,Масштабирование — только после пилота: ≥50 л/день и аптайм ≥95% в течение 3 месяцев,"locations, finance, telemetry",draft
0012-pilot-machine-sourcing,"Аппарат для пилота выбирать по котировкам: сравнить китайского производителя, местного дистрибьютора и европейский аппарат","hardware, water-treatment, finance",draft
0020-small-opaque-buffer-tank,Бак малый непрозрачный (20–40 л) с УФ и плановым сливом вместо бака 180 л,"hardware, water-treatment",draft
0021-heating-by-model,"Обогрев зависит от модели: уличные обогреваются зимой, внутренние — без обогрева","hardware",draft
0022-four-model-family,Четыре модели из одной базы и модулей: помещение/улица × стандарт/усиленная,"hardware",draft
0023-camera-all-models,Камера во всех моделях: по событиям и периодический контрольный снимок,"hardware, telemetry",draft
0024-auto-block-on-hygiene-alarm,"При загрязнении, вскрытии или серьёзной неисправности аппарат блокирует розлив и шлёт тревогу","hardware, telemetry, water-treatment",draft
0025-full-manufacturing-doc-pack,Документация — полный производственный пакет,"hardware, documentation",draft
0026-two-method-positioning,Позиционирование — два метода: рыночное по типу локации и физическое размещение внутри площадки,"locations, pricing",draft
0030-pilot-price-strategy,Пилот стартует с 10 RSD/л (50 RSD за 5 л); любое изменение цены — только ценовым экспериментом,"pricing, finance",draft
0031-pilot-buy-ready-made,Для пилота покупать готовый аппарат и сравнивать котировки по цене «от двери до двери»; сборка из компонентов отложена,"hardware, finance",draft
0032-straight-line-depreciation-stock-policy,"Оборудование амортизируется линейно по группам активов, запас считается по точке заказа с учётом товара в пути","finance, operations",draft
0033-procurement-policy,"Закупка — по письменным котировкам, с Incoterms, страхованием груза, документами на материалы и вторым источником критичных деталей","hardware, legal-tax, finance",draft
0040-certification-buy-vs-make,Для пилота сертификация идёт по пути «покупаем готовый аппарат»; «производим сами» пересматривать от ~20 точек,"hardware, water-treatment, legal-tax",draft
0041-master-certification-and-config-change,Стандартная конфигурация оформляется один раз как тип; изменения конфигурации классифицируются A/B/C,"hardware, operations, water-treatment",draft
0050-sampling-program-stages,"Программа проб воды идёт по этапам: пуск, ввод, рутина, периодический полный анализ, внеплановые","water-treatment, operations",draft
0051-sampling-rule-for-n-points,"При N точек микробиология — на каждой точке, химия и металлы — по кластерам «источник воды + конфигурация»","water-treatment, operations, locations",draft
0052-telemetry-triggers-unplanned-samples,"Телеметрия (TDS на выходе RO, температура и «возраст» воды в баке 30 л, отказ УФ, ресурс фильтров) запускает внеплановые пробы, но не заменяет лабораторию","telemetry, water-treatment, operations",draft
