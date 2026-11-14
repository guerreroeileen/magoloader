# -*- coding: utf-8 -*-
"""Estado compartido de la UI entre pestañas."""

import dataclasses
from typing import Any, Callable, List

from magoloader.constants import BRANDING_FILE
from magoloader.core.branding_settings import BrandingSettings, save_settings
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


class BrandingState:
    """
    Ajustes de personalización compartidos entre pestañas, con suscriptores.

    Se usa solo desde el hilo de la UI. Los hilos de descarga reciben una
    instantánea inmutable (`BrandingSettings.to_options()`).
    """

    def __init__(self, initial: BrandingSettings, path: str = BRANDING_FILE):
        self._settings = initial
        self._path = path
        self._subscribers: List[Callable[[BrandingSettings], None]] = []
        self._lock_count = 0
        self._lock_subscribers: List[Callable[[bool], None]] = []

    def get(self) -> BrandingSettings:
        """Devuelve los ajustes actuales."""
        return self._settings

    def update(self, *, persist: bool = True, force: bool = False, **changes: Any) -> None:
        """
        Cambia uno o más campos y notifica a los suscriptores si algo cambió.

        persist: guardar en disco ahora (False para ediciones por tecla; luego `save()`).
        force: notificar aunque los valores no cambien (p. ej. logo reemplazado en la misma ruta).
        """
        new = dataclasses.replace(self._settings, **changes)
        if new == self._settings and not force:
            return
        self._settings = new
        if persist:
            self.save()
        for callback in list(self._subscribers):
            callback(new)

    def save(self) -> None:
        """Guarda los ajustes actuales en disco (los errores de E/S se ignoran)."""
        try:
            save_settings(self._settings, self._path)
        except OSError:
            pass  # no poder guardar no debe impedir usar la app

    def subscribe(self, callback: Callable[[BrandingSettings], None]) -> None:
        """Registra un callback que recibe los ajustes nuevos en cada cambio."""
        self._subscribers.append(callback)

    def is_locked(self) -> bool:
        """True mientras haya alguna descarga en curso."""
        return self._lock_count > 0

    def set_locked(self, locked: bool) -> None:
        """Bloquea/desbloquea la edición (contador: varias descargas a la vez)."""
        was_locked = self.is_locked()
        if locked:
            self._lock_count += 1
        elif self._lock_count > 0:
            self._lock_count -= 1
        if self.is_locked() != was_locked:
            for callback in list(self._lock_subscribers):
                callback(self.is_locked())

    def subscribe_lock(self, callback: Callable[[bool], None]) -> None:
        """Registra un callback que recibe el nuevo estado de bloqueo."""
        self._lock_subscribers.append(callback)
