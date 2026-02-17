# -*- coding: utf-8 -*-
"""Internacionalización (i18n)."""

from magoloader.i18n.detector import get_current_language, set_language
from magoloader.i18n.translations import t

__all__ = ["t", "get_current_language", "set_language"]
