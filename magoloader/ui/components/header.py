# -*- coding: utf-8 -*-
"""Header de la pestaña Perfil: entrada de usuario y botón Analizar."""

from typing import Callable

from magoloader.i18n import t
from magoloader.ui.components.input_bar import InputBar


class Header(InputBar):
    """InputBar configurada para analizar un @usuario de TikTok."""

    def __init__(self, master, on_analyze: Callable[[], None], **kwargs):
        super().__init__(
            master,
            placeholder=t("header.username_placeholder"),
            button_text=t("header.analyze"),
            busy_text=t("header.analyzing"),
            on_submit=on_analyze,
            entry_width=280,
            **kwargs,
        )
        # Compatibilidad con el código existente
        self.entry_username = self.entry
        self.btn_analyze = self.button

    def get_username(self) -> str:
        return self.get_value()

    def set_analyzing(self, analyzing: bool) -> None:
        self.set_busy(analyzing)
