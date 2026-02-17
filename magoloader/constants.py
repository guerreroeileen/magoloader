# -*- coding: utf-8 -*-
"""Constantes de la aplicación."""

import os

# Diseño (estilo TikTok)
COLOR_BG = "#121212"
COLOR_ACCENT = "#FE2C55"
COLOR_ACCENT_HOVER = "#cc2444"
COLOR_CARD = "#1E1E1E"
COLOR_CARD_DARK = "#252525"
COLOR_TEXT = "#FFFFFF"
COLOR_TEXT_DIM = "#B0B0B0"
COLOR_OVERLAY = "#2a2a2a"
COLOR_PLACEHOLDER = "#333"

# UI
TITLE_MAX_LEN = 40
VIDEOS_PER_PAGE = 12
THUMBNAIL_WIDTH = 320
THUMBNAIL_HEIGHT = 180
CARD_WIDTH = 340

# Rutas
DEFAULT_SAVE_DIR = os.path.join(
    os.path.expanduser("~"), "Downloads", "MagoLoader"
)
CACHE_DIR = os.path.join(
    os.path.expanduser("~"), ".magoloader", "cache", "thumbnails"
)

# Ventana
WINDOW_TITLE = "MagoLoader"
WINDOW_GEOMETRY = "1100x700"
WINDOW_MINSIZE = (900, 600)

# Idiomas soportados (código ISO 639-1)
SUPPORTED_LANGUAGES = ("es", "en", "pt")
DEFAULT_LANGUAGE = "en"

# Analytics (Google Analytics 4)
GA_MEASUREMENT_ID = "G-Y3H384N20T"
GA_API_SECRET = "kz3UQZRbTDWa-oqFLuILew"

