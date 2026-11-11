# -*- coding: utf-8 -*-
"""Verifica que todas las traducciones estén completas en todos los idiomas soportados.

Comprueba que:
  - Cada idioma de SUPPORTED_LANGUAGES tenga un catálogo en TRANSLATIONS.
  - Todos los idiomas tengan exactamente las mismas claves.
  - Ninguna traducción esté vacía.
  - Los placeholders ({count}, {n}, ...) coincidan entre idiomas.

Uso:
  python scripts/check_i18n.py          # comprobación manual / CI
  python scripts/check_i18n.py --hook   # desde un hook de Claude Code (lee JSON por stdin)
"""

import json
import string
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

TRANSLATIONS_FILE = "magoloader/i18n/translations.py"


def _placeholders(text: str) -> set[str]:
    """Devuelve los nombres de los campos de formato de una cadena."""
    try:
        return {name for _, name, _, _ in string.Formatter().parse(text) if name}
    except ValueError:
        return set()


def find_problems() -> list[str]:
    """Devuelve una lista de problemas encontrados en el catálogo de traducciones."""
    from magoloader.constants import SUPPORTED_LANGUAGES
    from magoloader.i18n.translations import TRANSLATIONS

    problems: list[str] = []
    missing_langs = [lang for lang in SUPPORTED_LANGUAGES if lang not in TRANSLATIONS]
    for lang in missing_langs:
        problems.append(f"Language '{lang}' is in SUPPORTED_LANGUAGES but has no catalog in TRANSLATIONS.")

    langs = [lang for lang in SUPPORTED_LANGUAGES if lang in TRANSLATIONS]
    all_keys = set().union(*(TRANSLATIONS[lang].keys() for lang in langs)) if langs else set()

    for lang in langs:
        catalog = TRANSLATIONS[lang]
        for key in sorted(all_keys - catalog.keys()):
            problems.append(f"[{lang}] missing key '{key}'")
        for key, value in catalog.items():
            if not isinstance(value, str) or not value.strip():
                problems.append(f"[{lang}] empty translation for '{key}'")

    for key in sorted(all_keys):
        present = {lang: _placeholders(TRANSLATIONS[lang][key]) for lang in langs if key in TRANSLATIONS[lang]}
        if len({frozenset(p) for p in present.values()}) > 1:
            detail = ", ".join(f"{lang}={sorted(p)}" for lang, p in present.items())
            problems.append(f"placeholder mismatch for '{key}': {detail}")

    return problems


def main() -> int:
    if "--hook" in sys.argv:
        try:
            payload = json.load(sys.stdin)
        except (json.JSONDecodeError, ValueError):
            return 0
        file_path = str(payload.get("tool_input", {}).get("file_path", "")).replace("\\", "/")
        if not file_path.endswith(TRANSLATIONS_FILE):
            return 0

    try:
        problems = find_problems()
    except Exception as exc:  # error de sintaxis, import, etc.
        print(f"i18n check could not load translations: {exc}", file=sys.stderr)
        return 2

    if problems:
        print(
            "i18n check failed: every key must exist in all supported languages (es, en, pt).\n"
            + "\n".join(f"  - {p}" for p in problems),
            file=sys.stderr,
        )
        return 2
    if "--hook" not in sys.argv:
        print("i18n check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
