# -*- coding: utf-8 -*-
"""Selector de carpeta de guardado, sincronizado con SaveDirState."""

from tkinter import filedialog

import customtkinter as ctk

from magoloader.constants import COLOR_ACCENT, COLOR_ACCENT_HOVER, COLOR_TEXT_DIM
from magoloader.i18n import t
from magoloader.ui.state import SaveDirState
from magoloader.utils import truncate


class SaveFolderPicker(ctk.CTkFrame):
    """Título 'Carpeta de guardado', ruta actual y botón 'Examinar...'."""

    def __init__(self, master, save_dir_state: SaveDirState, max_path_len: int = 32, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._state = save_dir_state
        self._max_len = max_path_len

        ctk.CTkLabel(
            self,
            text=t("sidebar.save_location"),
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLOR_TEXT_DIM,
        ).pack(anchor="w", padx=4, pady=(8, 4))

        self.label_save_path = ctk.CTkLabel(
            self,
            text=truncate(save_dir_state.get(), max_path_len),
            font=ctk.CTkFont(size=11),
            text_color=COLOR_TEXT_DIM,
            anchor="w",
        )
        self.label_save_path.pack(fill="x", pady=(0, 8))

        ctk.CTkButton(
            self,
            text=t("sidebar.browse"),
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
            width=100,
            command=self._browse,
        ).pack(anchor="w", pady=(0, 16))

        save_dir_state.subscribe(self._on_dir_changed)

    def _browse(self) -> None:
        path = filedialog.askdirectory(
            initialdir=self._state.get(),
            title=t("sidebar.save_location"),
        )
        if path:
            self._state.set(path)

    def _on_dir_changed(self, path: str) -> None:
        self.label_save_path.configure(text=truncate(path, self._max_len))
