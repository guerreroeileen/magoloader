# -*- coding: utf-8 -*-
"""Detección del idioma del sistema."""

import locale
import os

from magoloader.constants import DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES


def _get_system_language() -> str:
    """Obtiene el código de idioma del sistema (ej: 'es', 'en')."""
    try:
        # Windows: getdefaultlocale() -> ('es_ES', 'cp1252') o ('en_US', 'UTF-8')
        lang, _ = locale.getdefaultlocale()
        if lang:
            code = lang.split("_")[0].lower()
            if code in SUPPORTED_LANGUAGES:
                return code
    except Exception:
        pass
    try:
        # Variables de entorno (Linux/macOS)
        lang = os.environ.get("LANG") or os.environ.get("LC_ALL") or ""
        if lang:
            code = lang.split("_")[0].split(".")[0].lower()
            if code in SUPPORTED_LANGUAGES:
                return code
    except Exception:
        pass
    return DEFAULT_LANGUAGE


_current = None


def get_current_language() -> str:
    """Devuelve el idioma actual (si no se ha fijado, detecta del sistema)."""
    global _current
    if _current is None:
        _current = _get_system_language()
    return _current


def set_language(code: str) -> None:
    """Fija el idioma (debe ser uno de SUPPORTED_LANGUAGES)."""
    global _current
    _current = code if code in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE
