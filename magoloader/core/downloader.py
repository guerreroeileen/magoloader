# -*- coding: utf-8 -*-
"""Lógica de extracción y descarga con yt-dlp."""

import os
import time
from typing import List, Optional

import yt_dlp


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
) -> None:
    """
    Descarga un video por URL en save_dir.
    outtmpl: plantilla yt-dlp (por defecto fecha_título.ext).
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
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])
