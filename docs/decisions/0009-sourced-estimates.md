---
id: 0009-sourced-estimates
title: Каждая строка сметы ссылается на [brief: X.X] или [source: ...]; голого TBD нет
status: draft
date: 2026-10-08
tags: [pipeline, finance]
track: process
fitness-functions:
  - pipeline/reviewer.py проверяет ссылки на бриф/источник и полноту строк
  - pipeline/verify.py требует источник у каждой строки и заполненный unit_price минимум в 80% строк каждого файла сметы
---

Мотивация: сметы идут в пакеты для банка, инвесторов и грантов, поэтому каждое число должно прослеживаться; пробелы сопровождаются диапазоном и источником.

Источник: reviewer.py, generator.py, примечания FINANCE.md, коммит 237d36c.
