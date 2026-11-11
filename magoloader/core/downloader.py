# -*- coding: utf-8 -*-
"""Lógica de extracción y descarga con yt-dlp."""

import os
import time
from typing import Callable, List, Optional

import yt_dlp
from yt_dlp.utils import DownloadError, ExtractorError


EXTRACT_RETRIES = 3
RETRY_DELAY_SEC = 2


def _base_opts() -> dict:
    """
    Opciones base para yt-dlp. Incluye impersonate (Chrome) para evitar
    errores SSL/TLS con TikTok; requiere: pip install "yt-dlp[curl-cffi]"
    """
    opts = {
        "quiet": True,
        "no_warnings": True,
        # Impersonar Chrome evita SSL TLSV1_ALERT_INTERNAL_ERROR con TikTok
        # "impersonate": "chrome",
    }
    return opts


def download_video(
    url: str,
    save_dir: str,
    outtmpl: Optional[str] = None,
    on_progress: Optional[Callable[[float], None]] = None,
) -> Optional[str]:
    """
    Descarga un video por URL en save_dir y devuelve la ruta del archivo guardado.
    outtmpl: plantilla yt-dlp (por defecto fecha_título.ext).
    on_progress: callback opcional con la fracción completada (0..1). Se invoca
        desde el hilo de descarga; el llamador debe pasar el resultado al hilo UI.
    """
    if not outtmpl:
        outtmpl = os.path.join(
            save_dir, "%(upload_date)s_%(title).100s.%(ext)s"
        )
    opts = _base_opts()
    opts.update({
        "outtmpl": outtmpl,
        "restrictfilenames": True,
    })
    if on_progress is not None:
        opts["progress_hooks"] = [_make_progress_hook(on_progress)]
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return _downloaded_path(ydl, info)
    except (DownloadError, ExtractorError) as e:
        raise RuntimeError(f"Error descargando el video: {e}") from e


def _make_progress_hook(on_progress: Callable[[float], None]) -> Callable[[dict], None]:
    """Convierte los eventos de progreso de yt-dlp en una fracción 0..1."""
    def hook(d: dict) -> None:
        status = d.get("status")
        if status == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            done = d.get("downloaded_bytes")
            if total and done is not None:
                on_progress(max(0.0, min(1.0, done / total)))
        elif status == "finished":
            on_progress(1.0)
    return hook


def _downloaded_path(ydl: "yt_dlp.YoutubeDL", info: Optional[dict]) -> Optional[str]:
    """Obtiene la ruta final del archivo descargado a partir del info de yt-dlp."""
    if not info:
        return None
    for item in info.get("requested_downloads") or []:
        path = item.get("filepath") or item.get("filename")
        if path:
            return path
    try:
        return ydl.prepare_filename(info)
    except Exception:
        return None
