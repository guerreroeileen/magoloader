# -*- coding: utf-8 -*-
"""Modelos de datos."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class VideoEntry:
    """Entrada de video (perfil o lista)."""
    url: str
    id: Optional[str] = None
    title: Optional[str] = None
    duration: Optional[float] = None
    thumbnail: Optional[str] = None


@dataclass
class ProfileInfo:
    """Información del perfil TikTok."""
    uploader: str
    username: str
    thumbnail: Optional[str] = None
    entries: List["VideoEntry"] = field(default_factory=list)
