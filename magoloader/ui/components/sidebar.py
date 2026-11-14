# -*- coding: utf-8 -*-
"""Sidebar con perfil, selector de carpeta y panel de personalización (con scroll)."""

import os
import customtkinter as ctk
from PIL import Image

from magoloader.constants import (
    COLOR_CARD,
    COLOR_CARD_DARK,
    COLOR_PLACEHOLDER,
    COLOR_TEXT,
    COLOR_TEXT_DIM,
)
from magoloader.i18n import t
from magoloader.ui.components.branding_panel import BrandingPanel
from magoloader.ui.components.save_folder_picker import SaveFolderPicker
from magoloader.ui.state import BrandingState, SaveDirState
from magoloader.ui.task_runner import TaskRunner


class Sidebar(ctk.CTkFrame):
    def __init__(
        self,
        master,
        save_dir_state: SaveDirState,
        branding_state: BrandingState,
        runner: TaskRunner,
        **kwargs,
    ):
        super().__init__(master, width=260, fg_color=COLOR_CARD, corner_radius=12, **kwargs)
        self.pack_propagate(False)

        # Contenido con scroll para que el panel de personalización quepa a 900x600
        body = ctk.CTkScrollableFrame(self, fg_color=COLOR_CARD, corner_radius=12)
        body.pack(fill="both", expand=True)

        ctk.CTkLabel(
            body,
            text=t("sidebar.profile"),
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLOR_TEXT_DIM,
        ).pack(anchor="w", padx=16, pady=(16, 8))

        self.profile_card = ctk.CTkFrame(body, fg_color=COLOR_CARD_DARK, corner_radius=10)
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

        self.folder_picker = SaveFolderPicker(body, save_dir_state=save_dir_state)
        self.folder_picker.pack(fill="x", padx=12)

        self.branding_panel = BrandingPanel(body, branding_state=branding_state, runner=runner)
        self.branding_panel.pack(fill="x", padx=8, pady=(0, 12))

    def set_profile(self, name: str, handle: str, count: int):
        self.profile_name.configure(text=name or "—")
        self.profile_handle.configure(text=f"@{handle}" if handle else "@")
        self.profile_count.configure(text=t("sidebar.videos_available", count=count))

    def set_profile_avatar(self, image_path: str):
        """Muestra la imagen de perfil desde una ruta local (llamar desde hilo UI)."""
        if not image_path or not os.path.isfile(image_path):
            return
        try:
            # CTkImage requiere objetos PIL, no rutas
            with Image.open(image_path) as img:
                pil_img = img.convert("RGB")
            self._avatar_image_ref = ctk.CTkImage(
                light_image=pil_img,
                dark_image=pil_img,
                size=(64, 64),
            )
            self.profile_avatar.configure(
                image=self._avatar_image_ref,
                text="",
                fg_color="transparent",
            )
        except Exception:
            pass
