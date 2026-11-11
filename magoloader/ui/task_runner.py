# -*- coding: utf-8 -*-
"""Ejecución de tareas en segundo plano y mensajes al usuario (compartido entre pestañas)."""

import queue
import threading
from tkinter import messagebox
from typing import Callable, Optional

from magoloader.core.analytics import Analytics
from magoloader.i18n import t
from magoloader.utils import is_ytdlp_extraction_error, is_ytdlp_ssl_error

ErrorMapper = Callable[[Exception], Optional[str]]


class TaskRunner:
    """
    Ejecuta trabajo en hilos y devuelve los resultados al hilo de la UI mediante una cola.

    Los hilos de trabajo NUNCA deben tocar widgets directamente: usan `post(callback)`
    y la ventana principal procesa la cola periódicamente con `process_pending()`.
    """

    def __init__(self, ui_queue: "queue.Queue[Callable[[], None]]", analytics: Analytics):
        self.queue = ui_queue
        self._analytics = analytics

    def post(self, callback: Callable[[], None]) -> None:
        """Encola un callback para ejecutarse en el hilo de la UI."""
        self.queue.put(callback)

    def process_pending(self) -> None:
        """Ejecuta los callbacks pendientes (llamar solo desde el hilo de la UI)."""
        try:
            while True:
                callback = self.queue.get_nowait()
                if callable(callback):
                    callback()
        except queue.Empty:
            pass

    def run(
        self,
        target: Callable[[], None],
        on_done: Optional[Callable[[], None]] = None,
        error_message: Optional[ErrorMapper] = None,
    ) -> None:
        """
        Ejecuta `target` en un hilo daemon.

        Si falla, muestra un mensaje traducido en este orden: error SSL, el mensaje
        de `error_message(exc)` (si se indica y devuelve texto), yt-dlp desactualizado,
        o el texto del error. `on_done` se encola siempre al terminar.
        """
        def wrapper() -> None:
            try:
                target()
            except Exception as exc:  # noqa: BLE001 - se muestra al usuario
                msg = self.map_error(exc, error_message)
                self.post(lambda m=msg: self.show_error(m))
            finally:
                if on_done:
                    self.post(on_done)

        threading.Thread(target=wrapper, daemon=True).start()

    @staticmethod
    def map_error(exc: Exception, error_message: Optional[ErrorMapper] = None) -> str:
        """Convierte una excepción en un mensaje traducido para el usuario."""
        if is_ytdlp_ssl_error(exc):
            return t("error.ytdlp_ssl")
        if error_message is not None:
            custom = error_message(exc)
            if custom:
                return custom
        if is_ytdlp_extraction_error(exc):
            return t("err_ytdlp_outdated")
        return str(exc) or repr(exc)

    def show_error(self, msg: str) -> None:
        """Muestra un error (hilo UI) y lo registra en analytics."""
        self._analytics.track_error("ui_error", msg)
        messagebox.showerror(t("dialog.error_title"), msg)

    def show_info(self, msg: str) -> None:
        """Muestra un mensaje informativo (hilo UI)."""
        messagebox.showinfo(t("app.title"), msg)
