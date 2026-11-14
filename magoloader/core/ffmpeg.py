# -*- coding: utf-8 -*-
"""Acceso al binario de FFmpeg y ejecución de subprocesos sin ventana de consola."""

import shutil
import subprocess
import sys
from typing import Any, List, Optional

_cached_path: Optional[str] = None


def get_ffmpeg_path() -> str:
    """
    Devuelve la ruta del ejecutable de FFmpeg.

    Usa primero el binario incluido en `imageio-ffmpeg` y, si no está disponible,
    el `ffmpeg` del PATH. Lanza RuntimeError si no se encuentra ninguno.
    """
    global _cached_path
    if _cached_path:
        return _cached_path
    path: Optional[str] = None
    try:
        import imageio_ffmpeg

        path = imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:  # noqa: BLE001 - se intenta el PATH a continuación
        path = None
    if not path:
        path = shutil.which("ffmpeg")
    if not path:
        raise RuntimeError("FFmpeg not found")
    _cached_path = path
    return path


def _hidden_kwargs(kwargs: dict) -> dict:
    """Añade las opciones para no abrir consola en Windows y sin stdin."""
    kwargs.setdefault("stdin", subprocess.DEVNULL)
    if sys.platform == "win32":
        flags = kwargs.get("creationflags", 0)
        kwargs["creationflags"] = flags | subprocess.CREATE_NO_WINDOW
    return kwargs


def run_hidden(args: List[str], **kwargs: Any) -> "subprocess.CompletedProcess":
    """subprocess.run sin ventana de consola (necesario en builds --noconsole)."""
    return subprocess.run(args, **_hidden_kwargs(kwargs))


def popen_hidden(args: List[str], **kwargs: Any) -> "subprocess.Popen":
    """subprocess.Popen sin ventana de consola (necesario en builds --noconsole)."""
    return subprocess.Popen(args, **_hidden_kwargs(kwargs))
