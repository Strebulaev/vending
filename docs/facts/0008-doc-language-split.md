---
id: 0008-doc-language-split
title: Сметы — на английском; остальная документация и база знаний — на русском
status: active
date: 2026-10-08
tags: [documentation]
kind: decision
governed-by: 0010-english-estimates
---

Консолидированные файлы пересобираются из английских смет скриптом `pipeline/consolidator.py`. Руководство по пилоту, TECH_SPEC, презентации и база знаний `docs/{facts,decisions,guardrails,skills,plans}` — на русском. Идентификаторы, ключи frontmatter и теги остаются латиницей.
