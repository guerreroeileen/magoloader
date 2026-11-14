# -*- coding: utf-8 -*-
"""Lógica de extracción y descarga con yt-dlp."""

import os
import time
from typing import Callable, List, Optional

import yt_dlp
from yt_dlp.utils import DownloadError, ExtractorError

from magoloader.core.branding import BrandingOptions, apply_branding


EXTRACT_RETRIES = 3
RETRY_DELAY_SEC = 2

# Con personalización, la descarga ocupa 0..DOWNLOAD_SHARE del progreso
# y la personalización el resto.
DOWNLOAD_SHARE = 0.6
STAGE_BRANDING = "branding"


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
    branding: Optional[BrandingOptions] = None,
    on_stage: Optional[Callable[[str], None]] = None,
) -> Optional[str]:
    """
    Descarga un video por URL en save_dir y devuelve la ruta del archivo guardado.
    outtmpl: plantilla yt-dlp (por defecto fecha_título.ext).
    on_progress: callback opcional con la fracción completada (0..1). Se invoca
        desde el hilo de descarga; el llamador debe pasar el resultado al hilo UI.
    branding: si se indica, se aplica la personalización tras la descarga
        (el progreso cubre ambas etapas). Si falla, se lanza BrandingError y el
        video sin personalizar se conserva.
    on_stage: callback opcional que recibe STAGE_BRANDING al empezar la
        personalización (desde el hilo de descarga).
    """
    if branding is None:
        return _download(url, save_dir, outtmpl, on_progress)

    def download_progress(fraction: float) -> None:
        if on_progress is not None:
            on_progress(fraction * DOWNLOAD_SHARE)

    def branding_progress(fraction: float) -> None:
        if on_progress is not None:
            on_progress(DOWNLOAD_SHARE + fraction * (1.0 - DOWNLOAD_SHARE))

    # Sobrescribir: si el archivo ya existe (quizá ya personalizado), se vuelve a
    # descargar el original para no aplicar la marca dos veces.
    path = _download(url, save_dir, outtmpl, download_progress, overwrite=True)
    if not path:
        raise RuntimeError("Error descargando el video: no se encontró el archivo")
    if on_stage is not None:
        on_stage(STAGE_BRANDING)
    return apply_branding(path, branding, on_progress=branding_progress)


def _download(
    url: str,
    save_dir: str,
    outtmpl: Optional[str],
    on_progress: Optional[Callable[[float], None]],
    overwrite: bool = False,
) -> Optional[str]:
    """Descarga con yt-dlp (sin personalización es el comportamiento original)."""
    if not outtmpl:
        outtmpl = os.path.join(
            save_dir, "%(upload_date)s_%(title).100s.%(ext)s"
        )
    opts = _base_opts()
    opts.update({
        "outtmpl": outtmpl,
        "restrictfilenames": True,
    })
    if overwrite:
        opts["overwrites"] = True
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
