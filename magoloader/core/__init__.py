# -*- coding: utf-8 -*-
"""Lógica de negocio (yt-dlp, modelos)."""

from magoloader.core.downloader import download_video
from magoloader.core.models import ProfileInfo, VideoEntry

__all__ = [
    "download_video",
    "ProfileInfo",
    "VideoEntry",
]
