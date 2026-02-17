# -*- coding: utf-8 -*-
"""Card de video con miniatura, duración, título y selección (clic en miniatura)."""

import customtkinter as ctk
from typing import Any, Callable, Optional

from magoloader.constants import (
    CARD_WIDTH,
    COLOR_ACCENT,
    COLOR_ACCENT_HOVER,
    COLOR_CARD_DARK,
    COLOR_OVERLAY,
    COLOR_PLACEHOLDER,
    COLOR_TEXT,
    COLOR_TEXT_DIM,
    THUMBNAIL_HEIGHT,
    THUMBNAIL_WIDTH,
)
from magoloader.i18n import t
from magoloader.utils import format_duration, truncate
from magoloader.constants import TITLE_MAX_LEN
from magoloader.ui.thumbnail_loader import load_video_thumbnail_async


class VideoCard(ctk.CTkFrame):
    """
    Card de un video. Muestra miniatura (o placeholder), duración y título.
    Clic en la miniatura alterna la selección para descarga.
    """

    def __init__(
        self,
        master,
        entry: dict,
        var: ctk.BooleanVar,
        on_toggle: Callable[[], None],
        ui_update_queue: Any,
        **kwargs,
    ):
        super().__init__(
            master,
            fg_color=COLOR_CARD_DARK,
            corner_radius=10,
            width=CARD_WIDTH,
            **kwargs,
        )
        self.grid_propagate(False)
        self._entry = entry
        self._var = var
        self._on_toggle = on_toggle
        self._ui_queue = ui_update_queue
        self._image_ref = None  # mantener referencia para que no se borre la imagen

        # Contenedor de la miniatura (clicable)
        self.thumb_frame = ctk.CTkFrame(
            self,
            fg_color=COLOR_PLACEHOLDER,
            corner_radius=8,
            width=THUMBNAIL_WIDTH,
            height=THUMBNAIL_HEIGHT,
        )
        self.thumb_frame.place(x=8, y=8)
        self.thumb_frame.bind("<Button-1>", self._on_thumb_click)
        self.thumb_frame.bind("<Enter>", lambda e: self.thumb_frame.configure(cursor="hand2"))
        self.thumb_frame.bind("<Leave>", lambda e: self.thumb_frame.configure(cursor=""))

        # Label para imagen o placeholder (dentro del frame para que el clic funcione)
        self.thumb_label = ctk.CTkLabel(
            self.thumb_frame,
            text="▶",
            font=ctk.CTkFont(size=32),
            text_color=COLOR_TEXT_DIM,
            fg_color="transparent",
            width=THUMBNAIL_WIDTH,
            height=THUMBNAIL_HEIGHT,
        )
        self.thumb_label.place(x=0, y=0)
        self.thumb_label.bind("<Button-1>", self._on_thumb_click)
        self.thumb_label.bind("<Enter>", lambda e: self.thumb_label.configure(cursor="hand2"))

        # Checkbox (compartido con el padre para selección)
        self.cb = ctk.CTkCheckBox(
            self,
            text="",
            variable=var,
            width=24,
            height=24,
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
            command=self._on_checkbox_change,
        )
        self.cb.place(relx=1.0, x=-36, y=8, anchor="ne")

        # Duración
        dur = format_duration(entry.get("duration"))
        self.dur_label = ctk.CTkLabel(
            self,
            text=dur,
            font=ctk.CTkFont(size=11),
            text_color=COLOR_TEXT,
            fg_color=COLOR_OVERLAY,
        )
        self.dur_label.place(x=12, y=8 + THUMBNAIL_HEIGHT - 22)

        # Título
        title = entry.get("title") or t("video.no_title")
        title = truncate(title, 35)
        ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(size=12),
            text_color=COLOR_TEXT,
            wraplength=200,
            anchor="w",
            justify="left",
        ).pack(padx=12, pady=(8, 12), fill="x", anchor="w")

        # Cargar miniatura en segundo plano (URL directa o vía oEmbed si no hay)
        if self._ui_queue is not None:
            load_video_thumbnail_async(
                video_url=entry.get("url", ""),
                thumbnail_url=entry.get("thumbnail"),
                on_loaded=self._on_thumbnail_loaded,
            )

    def _on_thumb_click(self, event=None):
        self._var.set(not self._var.get())
        self._on_toggle()

    def _on_checkbox_change(self):
        self._on_toggle()

    def _on_thumbnail_loaded(self, path: Optional[str]):
        """Llamado desde el hilo del loader; encola actualización en el hilo de UI."""
        if path and self._ui_queue is not None:
            self._ui_queue.put(lambda: self._set_thumbnail(path))

    def _set_thumbnail(self, path: str):
        """Llamar solo desde el hilo de UI. Muestra la imagen en thumb_label."""
        try:
            self._image_ref = ctk.CTkImage(
                light_image=path,
                dark_image=path,
                size=(THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT),
            )
            self.thumb_label.configure(image=self._image_ref, text="")
            self.thumb_label.configure(fg_color="transparent")
        except Exception:
            pass

    def get_entry(self) -> dict:
        return self._entry
