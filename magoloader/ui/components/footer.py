# -*- coding: utf-8 -*-
"""Footer con botón de descarga y barra de progreso."""

import customtkinter as ctk

from magoloader.constants import COLOR_ACCENT, COLOR_TEXT_DIM
from magoloader.i18n import t


class Footer(ctk.CTkFrame):
    def __init__(self, master, on_download, **kwargs):
        super().__init__(master, fg_color="transparent", height=80, **kwargs)
        self.pack_propagate(False)
        self._on_download = on_download

        self.btn_download = ctk.CTkButton(
            self,
            text=t("footer.download", n=0),
            fg_color=COLOR_ACCENT,
            hover_color="#cc2444",
            height=44,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=on_download,
        )
        self.btn_download.pack(fill="x", pady=(0, 8))

        self.progress_bar = ctk.CTkProgressBar(
            self,
            progress_color=COLOR_ACCENT,
            fg_color="#333",
            height=10,
        )
        self.progress_bar.pack(fill="x")
        self.progress_bar.set(0)

        self.label_progress = ctk.CTkLabel(
            self,
            text=t("footer.progress", pct=0),
            font=ctk.CTkFont(size=12),
            text_color=COLOR_TEXT_DIM,
        )
        self.label_progress.pack(anchor="w", pady=(4, 0))

    def set_download_label(self, n: int):
        self.btn_download.configure(text=t("footer.download", n=n))

    def set_progress(self, fraction: float):
        self.progress_bar.set(fraction)
        self.label_progress.configure(text=t("footer.progress", pct=int(fraction * 100)))

    def set_download_enabled(self, enabled: bool):
        self.btn_download.configure(state="normal" if enabled else "disabled")
