# -*- coding: utf-8 -*-
"""Header con entrada de usuario y botón Analizar."""

import customtkinter as ctk

from magoloader.constants import COLOR_ACCENT, COLOR_ACCENT_HOVER, COLOR_CARD, COLOR_TEXT
from magoloader.i18n import t


class Header(ctk.CTkFrame):
    def __init__(self, master, on_analyze, **kwargs):
        super().__init__(master, fg_color="transparent", height=56, **kwargs)
        self.pack_propagate(False)
        self._on_analyze = on_analyze

        ctk.CTkLabel(
            self,
            text=t("app.title"),
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=COLOR_TEXT,
        ).pack(side="left", padx=(0, 24))

        self.entry_username = ctk.CTkEntry(
            self,
            placeholder_text=t("header.username_placeholder"),
            width=280,
            height=36,
            border_color=COLOR_ACCENT,
            fg_color=COLOR_CARD,
            text_color=COLOR_TEXT,
        )
        self.entry_username.pack(side="left", padx=(0, 12))
        self.entry_username.bind("<Return>", lambda e: on_analyze())

        self.btn_analyze = ctk.CTkButton(
            self,
            text=t("header.analyze"),
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
            width=100,
            height=36,
            command=on_analyze,
        )
        self.btn_analyze.pack(side="left")

    def get_username(self) -> str:
        return self.entry_username.get().strip()

    def set_analyzing(self, analyzing: bool):
        if analyzing:
            self.btn_analyze.configure(state="disabled", text=t("header.analyzing"))
        else:
            self.btn_analyze.configure(state="normal", text=t("header.analyze"))
