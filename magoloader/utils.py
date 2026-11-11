# -*- coding: utf-8 -*-
"""Utilidades generales."""

import re
from pathlib import Path
from typing import Optional
from urllib.parse import urlsplit, urlunsplit

# Hosts de TikTok aceptados (comparación exacta, evita dominios look-alike)
_TIKTOK_MAIN_HOSTS = {"tiktok.com", "www.tiktok.com", "m.tiktok.com"}
_TIKTOK_SHORT_HOSTS = {"vm.tiktok.com", "vt.tiktok.com"}
_TIKTOK_MAIN_PATHS = (
    re.compile(r"^/@[^/]+/video/\d+/?$"),
    re.compile(r"^/t/[A-Za-z0-9_-]+/?$"),
    re.compile(r"^/v/\d+\.html$"),
)
_TIKTOK_SHORT_PATH = re.compile(r"^/[A-Za-z0-9_-]+/?$")


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


def normalize_tiktok_video_url(text: str) -> Optional[str]:
    """
    Valida localmente (sin red) que el texto sea un enlace a un video de TikTok.
    Devuelve la URL normalizada (https://...) o None si no es válida.
    """
    if not text:
        return None
    raw = text.strip()
    if not raw or any(c.isspace() for c in raw):
        return None
    if "://" not in raw:
        raw = "https://" + raw
    try:
        parts = urlsplit(raw)
    except ValueError:
        return None
    if parts.scheme.lower() not in ("http", "https"):
        return None
    if parts.username or parts.password or parts.port:
        return None
    host = (parts.hostname or "").lower()
    path = parts.path or "/"
    if host in _TIKTOK_MAIN_HOSTS:
        if not any(p.match(path) for p in _TIKTOK_MAIN_PATHS):
            return None
    elif host in _TIKTOK_SHORT_HOSTS:
        if not _TIKTOK_SHORT_PATH.match(path):
            return None
    else:
        return None
    return urlunsplit(("https", host, path, parts.query, ""))
