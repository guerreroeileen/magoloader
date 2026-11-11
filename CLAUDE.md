# MagoLoader

Desktop app (Python 3.10+, CustomTkinter, yt-dlp) to download TikTok videos without watermark. Packaged with PyInstaller.

## Spec-driven workflow (OpenSpec)

- This project uses **OpenSpec**. Before building a feature or changing behavior, read `openspec/config.yaml` (project context and rules) and the relevant specs in `openspec/specs/<area>/spec.md` (`core`, `ui`, `i18n`).
- New features go through a change: `/opsx:propose` → `/opsx:apply` → `/opsx:archive` (skills in `.claude/skills/openspec-*`). Active changes live in `openspec/changes/`.
- Follow the rules in `openspec/config.yaml` for every artifact (proposal, design, tasks) and operation (apply, archive).
- Python style: follow the `python-code-style` and `python-project-structure` skills. Every file starts with `# -*- coding: utf-8 -*-`, uses docstrings and explicit type hints.

## Translations (mandatory)

Supported languages: **es, en, pt** (`SUPPORTED_LANGUAGES` in `magoloader/constants.py`).

- Never hardcode user-facing text. Use `t("area.key")` from `magoloader/i18n/translations.py`.
- Every new or changed key MUST be added to **all three** catalogs (`es`, `en`, `pt`) in the same change, with the same `{placeholders}`, and with a real translation (not a copy of another language).
- When renaming or removing a key, update it in all languages.
- Run `python scripts/check_i18n.py` (or `python -m unittest discover -s tests`) before finishing. A hook runs this check automatically after every edit to `translations.py`.
- Adding a new language means: add it to `SUPPORTED_LANGUAGES`, add a full catalog, and update `openspec/specs/i18n/spec.md`.

## Architecture

- `magoloader/core/`: extractors (factory pattern), downloader, models, updater, analytics (GA4).
- `magoloader/ui/`: CustomTkinter app and components.
- `magoloader/i18n/`: locale detection and translations.
- Entry point: `main.py`. Build: `python build.py` (PyInstaller, `MagoLoader.spec`).

## Rules

- Network calls, thumbnail loading, update checks and downloads MUST run in background threads. Never block the Tk main loop.
- Show errors through UI popups or status labels (translated), never crash the window.
- Bump `magoloader/version.py` and add an entry to `CHANGELOG.md` for user-facing releases.
