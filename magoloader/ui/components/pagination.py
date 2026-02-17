# -*- coding: utf-8 -*-
"""Barra de paginación."""

import customtkinter as ctk

from magoloader.constants import COLOR_ACCENT, COLOR_ACCENT_HOVER, COLOR_TEXT_DIM
from magoloader.i18n import t


class PaginationBar(ctk.CTkFrame):
    def __init__(self, master, on_prev, on_next, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._on_prev = on_prev
        self._on_next = on_next

        self.btn_prev = ctk.CTkButton(
            self,
            text=t("pagination.prev"),
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
            width=100,
            command=on_prev,
        )
        self.btn_prev.pack(side="left", padx=(0, 12))

        self.label_page = ctk.CTkLabel(
            self,
            text=t("pagination.page", current=1, total=1),
            font=ctk.CTkFont(size=13),
            text_color=COLOR_TEXT_DIM,
        )
        self.label_page.pack(side="left", padx=12)

        self.btn_next = ctk.CTkButton(
            self,
            text=t("pagination.next"),
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
            width=100,
            command=on_next,
        )
        self.btn_next.pack(side="left")

    def update_state(self, current_page: int, total_pages: int):
        self.label_page.configure(
            text=t("pagination.page", current=current_page + 1, total=total_pages)
        )
        self.btn_prev.configure(state="normal" if current_page > 0 else "disabled")
        self.btn_next.configure(
            state="normal" if current_page < total_pages - 1 and total_pages > 1 else "disabled"
        )
        if total_pages <= 1:
            self.btn_prev.configure(state="disabled")
            self.btn_next.configure(state="disabled")
