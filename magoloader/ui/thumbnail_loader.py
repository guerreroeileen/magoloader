# -*- coding: utf-8 -*-
"""Carga y caché de miniaturas desde URL. Fallback vía oEmbed para TikTok."""

import hashlib
import json
import os
import threading
import urllib.parse
from typing import Callable, Optional
from urllib.request import Request, urlopen

from magoloader.constants import CACHE_DIR
from magoloader.utils import ensure_dir

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def _cache_path(url: str, ext: str = "jpg") -> str:
    """Ruta de archivo en caché para una URL."""
    ensure_dir(CACHE_DIR)
    key = hashlib.sha256(url.encode()).hexdigest()[:16]
    return os.path.join(CACHE_DIR, f"{key}.{ext}")


def load_thumbnail_sync(url: str) -> Optional[str]:
    """
    Descarga la miniatura desde url y guarda en caché.
    Devuelve la ruta del archivo local o None si falla.
    """
    if not url or not url.startswith("http"):
        return None
    path_lower = url.split("?")[0].lower()
    ext = "webp" if ".webp" in path_lower else "jpg"
    path = _cache_path(url, ext)
    if os.path.isfile(path):
        return path
    try:
        req = Request(url, headers={"User-Agent": USER_AGENT})
        with urlopen(req, timeout=15) as resp:
            data = resp.read()
        ensure_dir(CACHE_DIR)
        with open(path, "wb") as f:
            f.write(data)
        return path
    except Exception:
        return None


def get_tiktok_thumbnail_url(video_url: str) -> Optional[str]:
    """
    Obtiene la URL de la miniatura de un video TikTok vía oEmbed.
    No requiere API key. Devuelve None si falla.
    """
    if not video_url or "tiktok.com" not in video_url:
        return None
    try:
        oembed_url = "https://www.tiktok.com/oembed?url=" + urllib.parse.quote(video_url)
        req = Request(oembed_url, headers={"User-Agent": USER_AGENT})
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        return data.get("thumbnail_url") or data.get("thumbnail")
    except Exception:
        return None


def load_thumbnail_async(url: str, on_loaded: Callable[[Optional[str]], None]) -> None:
    """Carga la miniatura en un hilo y llama on_loaded(path) en ese hilo."""
    def work():
        path = load_thumbnail_sync(url)
        on_loaded(path)

    threading.Thread(target=work, daemon=True).start()


def load_video_thumbnail_async(
    video_url: str,
    thumbnail_url: Optional[str],
    on_loaded: Callable[[Optional[str]], None],
) -> None:
    """
    Carga la miniatura de un video: usa thumbnail_url si existe,
    si no obtiene la URL vía oEmbed (TikTok) y luego descarga.
    on_loaded(path) se llama desde un hilo de trabajo.
    """
    def work():
        url = thumbnail_url
        if not url or not url.startswith("http"):
            url = get_tiktok_thumbnail_url(video_url)
        path = load_thumbnail_sync(url) if url else None
        on_loaded(path)

    threading.Thread(target=work, daemon=True).start()
