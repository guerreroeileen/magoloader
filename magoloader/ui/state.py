# -*- coding: utf-8 -*-
"""Estado compartido de la UI entre pestañas."""

from typing import Callable, List

from magoloader.utils import ensure_dir


class SaveDirState:
    """Carpeta de guardado única para toda la aplicación, con suscriptores."""

    def __init__(self, initial: str):
        self._path = initial
        self._subscribers: List[Callable[[str], None]] = []
        ensure_dir(initial)

    def get(self) -> str:
        """Devuelve la carpeta de guardado actual."""
        return self._path

    def set(self, path: str) -> None:
        """Cambia la carpeta (la crea si no existe) y notifica a los suscriptores."""
        if not path:
            return
        ensure_dir(path)
        self._path = path
        for callback in list(self._subscribers):
            callback(path)

    def subscribe(self, callback: Callable[[str], None]) -> None:
        """Registra un callback que recibe la nueva ruta en cada cambio."""
        self._subscribers.append(callback)
