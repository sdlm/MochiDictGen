# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MochiDictGen — система генерации английских словарных карточек для Mochi SRS (mochi.cards). Цель: создать ~6000 карточек для изучения английского от A2 до C1.

## Language

Документация и общение с пользователем — на русском. Содержимое карточек: Definition, Example, Collocations, Synonyms & Nuance, Cloze — на английском; Translation — на русском.

## Documentation

- `docs/decks.md` — структура колод, объёмы слов по уровням
- `docs/template.md` — шаблон карточки (8 полей), пример заполнения
- `docs/data-format.md` — формат JSON-файлов в `data/`, маппинг на шаблон Mochi
- `docs/field-guidelines.md` — требования к содержимому каждого поля карточки
- `docs/plan.md` — план обучения, темп, сроки

**Всегда читай docs/ перед генерацией карточек.**

## MCP Integration

Проект работает через MCP-сервер `@fredrika/mcp-mochi` (конфигурация — `.mcp.json`). Доступные операции:
- Управление карточками: `create_flashcard`, `create_card_from_template`, `update_flashcard`, `delete_flashcard`, `archive_flashcard`
- Чтение: `list_decks`, `list_flashcards`, `list_templates`, `get_template`, `get_due_cards`

API не поддерживает создание/удаление колод и не возвращает иерархию (parent-child) колод.

## Card Generation Workflow

### 1. Генерация JSON

Claude генерирует слова пакетами по 50–100 штук и сохраняет в `data/<level>.json` (сейчас существует `data/a2.json`). Формат — массив объектов, схема в `docs/data-format.md`.

При генерации:
- Читать `docs/field-guidelines.md` для соблюдения формата полей
- Читать существующие слова в целевом файле, чтобы не дублировать
- Порядок: A2 (beginner → intermediate → advance) → B1 → B2 → C1

### 2. Загрузка в Mochi

Два способа загрузки:

**Скрипт `scripts/upload.py`** — пакетная загрузка через Mochi REST API:
```bash
python3 scripts/upload.py --dry-run data/a2.json   # проверка
python3 scripts/upload.py data/a2.json              # загрузка
```
Зависимости: Python 3.11+, `requests`. Управление через Poetry (`pyproject.toml`).

**MCP `create_card_from_template`** — поштучная загрузка прямо из Claude Code.

### 3. Шаблон и колоды

Шаблон: **Custom template**. Поля шаблона:
Word, Part of speech, Definition, Example, Translation, Collocations, Synonyms & Nuance, Cloze.

Колоды организованы по CEFR-уровням (A2/B1/B2/C1), каждый разбит на beginner/intermediate/advance. Структура колод — в `docs/decks.md`.

## Project Structure

```
data/           — JSON-файлы со словами (по уровням)
docs/           — документация (колоды, шаблон, формат, гайдлайны, план)
scripts/        — upload.py (пакетная загрузка в Mochi)
.mcp.json       — конфигурация MCP-сервера mochi
pyproject.toml  — Python-зависимости (Poetry)
```
