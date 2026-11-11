# -*- coding: utf-8 -*-
"""Barra reutilizable: campo de texto + botón de acción con estado ocupado."""

from typing import Callable, Optional

import customtkinter as ctk

from magoloader.constants import COLOR_ACCENT, COLOR_ACCENT_HOVER, COLOR_CARD, COLOR_TEXT


class InputBar(ctk.CTkFrame):
    """
    Campo de entrada con botón. Enter envía. Mientras está ocupado el botón
    se desactiva y muestra `busy_text`.
    """

    def __init__(
        self,
        master,
        placeholder: str,
        button_text: str,
        busy_text: str,
        on_submit: Callable[[], None],
        entry_width: Optional[int] = None,
        **kwargs,
    ):
        super().__init__(master, fg_color="transparent", height=56, **kwargs)
        self.pack_propagate(False)
        self._button_text = button_text
        self._busy_text = busy_text
        self._on_submit = on_submit

        self.entry = ctk.CTkEntry(
            self,
            placeholder_text=placeholder,
            width=entry_width or 280,
            height=36,
            border_color=COLOR_ACCENT,
            fg_color=COLOR_CARD,
            text_color=COLOR_TEXT,
        )
        if entry_width is None:
            self.entry.pack(side="left", fill="x", expand=True, padx=(0, 12))
        else:
            self.entry.pack(side="left", padx=(0, 12))
        self.entry.bind("<Return>", lambda e: self._submit())

        self.button = ctk.CTkButton(
            self,
            text=button_text,
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
            width=100,
            height=36,
            command=self._submit,
        )
        self.button.pack(side="left")

    def _submit(self) -> None:
        if str(self.button.cget("state")) == "disabled":
            return
        self._on_submit()

    def get_value(self) -> str:
        """Texto actual del campo, sin espacios alrededor."""
        return self.entry.get().strip()

    def set_busy(self, busy: bool) -> None:
        """Activa/desactiva el estado ocupado del botón."""
        if busy:
            self.button.configure(state="disabled", text=self._busy_text)
        else:
            self.button.configure(state="normal", text=self._button_text)

    def set_enabled(self, enabled: bool) -> None:
        """Activa/desactiva el botón sin cambiar su texto."""
        self.button.configure(state="normal" if enabled else "disabled")

    def bind_change(self, callback: Callable[[], None]) -> None:
        """
        Llama a `callback` (en el hilo UI, tras aplicar el cambio) cada vez que el
        texto se modifica: teclado, pegar, cortar o borrado.
        """
        def on_edit() -> bool:
            self.after_idle(callback)
            return True  # nunca bloquea la edición

        inner = self.entry._entry  # tkinter.Entry interno de CTkEntry
        inner.configure(validate="key", validatecommand=(inner.register(on_edit),))
