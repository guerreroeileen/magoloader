# -*- coding: utf-8 -*-
"""Utilidades generales."""

import re
from pathlib import Path


def ensure_dir(path: str) -> None:
    """Crea el directorio y padres si no existen."""
    Path(path).mkdir(parents=True, exist_ok=True)


def sanitize_filename(name: str) -> str:
    """Elimina caracteres no válidos para nombres de archivo en Windows."""
    name = re.sub(r'[<>:"/\\|?*]', "_", name)
    return name.strip(" .") or "video"


def format_duration(seconds) -> str:
    """Convierte segundos a MM:SS."""
    if seconds is None or seconds < 0:
        return "0:00"
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"


def truncate(text: str, max_len: int) -> str:
    """Trunca texto con '...' si excede max_len."""
    if not text:
        return ""
    text = str(text).strip()
    return (text[: max_len - 3] + "...") if len(text) > max_len else text


def is_ytdlp_extraction_error(exc: Exception) -> bool:
    """Detecta el error típico de TikTok / extracción de yt-dlp."""
    msg = str(exc).lower()
    return (
        "unable to extract" in msg
        or "please report this issue" in msg
        or "please report" in msg
    )


def is_ytdlp_ssl_error(exc: Exception) -> bool:
    """Detecta errores SSL/TLS (ej. TLSV1_ALERT_INTERNAL_ERROR con TikTok)."""
    msg = str(exc).lower()
    return "ssl" in msg or "tls" in msg or "certificate" in msg
