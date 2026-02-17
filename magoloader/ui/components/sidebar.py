# -*- coding: utf-8 -*-
"""Sidebar con perfil y selector de carpeta."""

import os
import customtkinter as ctk

from magoloader.constants import (
    COLOR_ACCENT,
    COLOR_ACCENT_HOVER,
    COLOR_CARD,
    COLOR_CARD_DARK,
    COLOR_PLACEHOLDER,
    COLOR_TEXT,
    COLOR_TEXT_DIM,
)
from magoloader.i18n import t
from magoloader.utils import truncate


class Sidebar(ctk.CTkFrame):
    def __init__(self, master, save_dir: str, on_browse, **kwargs):
        super().__init__(master, width=260, fg_color=COLOR_CARD, corner_radius=12, **kwargs)
        self.pack_propagate(False)
        self._save_dir = save_dir
        self._on_browse = on_browse

        ctk.CTkLabel(
            self,
            text=t("sidebar.profile"),
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLOR_TEXT_DIM,
        ).pack(anchor="w", padx=16, pady=(16, 8))

        self.profile_card = ctk.CTkFrame(self, fg_color=COLOR_CARD_DARK, corner_radius=10)
        self.profile_card.pack(fill="x", padx=12, pady=(0, 16))

        self._avatar_image_ref = None  # referencia para que no se borre la imagen
        self.profile_avatar = ctk.CTkLabel(
            self.profile_card,
            text="?",
            width=64,
            height=64,
            fg_color=COLOR_PLACEHOLDER,
            corner_radius=32,
            font=ctk.CTkFont(size=24),
            text_color=COLOR_TEXT_DIM,
        )
        self.profile_avatar.pack(pady=(16, 8))

        self.profile_name = ctk.CTkLabel(
            self.profile_card,
            text="—",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLOR_TEXT,
        )
        self.profile_name.pack()
        self.profile_handle = ctk.CTkLabel(
            self.profile_card,
            text="@",
            font=ctk.CTkFont(size=12),
            text_color=COLOR_TEXT_DIM,
        )
        self.profile_handle.pack()
        self.profile_count = ctk.CTkLabel(
            self.profile_card,
            text=t("sidebar.videos_available", count=0),
            font=ctk.CTkFont(size=12),
            text_color=COLOR_TEXT_DIM,
        )
        self.profile_count.pack(pady=(0, 16))

        ctk.CTkLabel(
            self,
            text=t("sidebar.save_location"),
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLOR_TEXT_DIM,
        ).pack(anchor="w", padx=16, pady=(8, 4))

        path_frame = ctk.CTkFrame(self, fg_color="transparent")
        path_frame.pack(fill="x", padx=12, pady=(0, 8))

        self.label_save_path = ctk.CTkLabel(
            path_frame,
            text=truncate(save_dir, 32),
            font=ctk.CTkFont(size=11),
            text_color=COLOR_TEXT_DIM,
            anchor="w",
        )
        self.label_save_path.pack(side="left", fill="x", expand=True)

        ctk.CTkButton(
            self,
            text=t("sidebar.browse"),
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
            width=100,
            command=on_browse,
        ).pack(anchor="w", padx=12, pady=(0, 16))

    def set_profile(self, name: str, handle: str, count: int):
        self.profile_name.configure(text=name or "—")
        self.profile_handle.configure(text=f"@{handle}" if handle else "@")
        self.profile_count.configure(text=t("sidebar.videos_available", count=count))

    def set_profile_avatar(self, image_path: str):
        """Muestra la imagen de perfil desde una ruta local (llamar desde hilo UI)."""
        if not image_path or not os.path.isfile(image_path):
            return
        try:
            self._avatar_image_ref = ctk.CTkImage(
                light_image=image_path,
                dark_image=image_path,
                size=(64, 64),
            )
            self.profile_avatar.configure(
                image=self._avatar_image_ref,
                text="",
                fg_color="transparent",
            )
        except Exception:
            pass

    def set_save_dir(self, path: str):
        self._save_dir = path
        self.label_save_path.configure(text=truncate(path, 38))
