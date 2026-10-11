# Управление артефактами через GitHub CLI

Пять задач по артефактам пилота имеют канонические заголовки и тексты в `config/artifact-issues.json` и `.github/artifact-issues/`. Это позволяет повторно создавать недостающие issues и сверять их с локальным планом, не создавая дубликатов.

| Этап | GitHub issue | Артефакт |
|---|---|---|
| 1 | [#1](https://github.com/Strebulaev/vending/issues/1) | Бизнес-модель |
| 2 | [#4](https://github.com/Strebulaev/vending/issues/4) | Техническая спецификация оборудования водомата |
| 3 | [#2](https://github.com/Strebulaev/vending/issues/2) | Критерии и скоринг точек |
| 4 | [#5](https://github.com/Strebulaev/vending/issues/5) | Обязательный порядок допуска водомата к запуску |
| 5 | [#3](https://github.com/Strebulaev/vending/issues/3) | Финансовая модель и unit economics |

Карточки 2 и 4 сформулированы как техническая спецификация оборудования и конкретный порядок получения допуска к запуску соответственно.

## Требования

- Установленный GitHub CLI `gh`, вход через `gh auth login` и право создавать issues в `Strebulaev/vending`.
- Команды выполнять из корня репозитория. Скрипт использует системный Python 3 и не требует внешних пакетов.

## Команды

```bash
# Показать статус каждой из пяти задач; отсутствующие будут отмечены MISSING
python3 pipeline/manage_artifact_issues.py list

# Создать только отсутствующие задачи (повторный запуск безопасен)
python3 pipeline/manage_artifact_issues.py create

# Посмотреть общий список GitHub issues
gh issue list --repo Strebulaev/vending --state all

# Открыть конкретную задачу и комментарии
gh issue view <номер> --repo Strebulaev/vending --comments

# Обновить статус и поля задачи
gh issue edit <номер> --repo Strebulaev/vending --title "Новый заголовок"
gh issue close <номер> --repo Strebulaev/vending --comment "Критерии DoD выполнены; доказательства: <ссылки на commit/run>"
gh issue reopen <номер> --repo Strebulaev/vending

# Запустить воспроизводимый расчет после попадания workflow в default branch
gh workflow run business-model-calculation.yml --repo Strebulaev/vending
gh run list --repo Strebulaev/vending --workflow business-model-calculation.yml
gh run watch <run-id> --repo Strebulaev/vending

# Проверить/собрать четыре спецификации конфигураций
python3 pipeline/build_equipment_specs.py --check
gh workflow run equipment-specifications.yml --repo Strebulaev/vending
gh run list --repo Strebulaev/vending --workflow equipment-specifications.yml
```

Закрывать задачу следует только после выполнения чек-листа в issue и ссылки на подтверждения. «Не найдено» допустимо как честный статус открытого входа, но не заменяет обязательный гейт законности, безопасности, бюджета или решения владельца. Тексты для будущих изменений сначала редактируются в репозитории; после review issue можно синхронизировать командой `gh issue edit --body-file <файл>`.
