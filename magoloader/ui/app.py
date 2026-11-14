# -*- coding: utf-8 -*-
"""Ventana principal de MagoLoader: contenedor de pestañas y servicios compartidos."""

import os
import queue

import customtkinter as ctk

from magoloader.constants import (
    COLOR_ACCENT,
    COLOR_ACCENT_HOVER,
    COLOR_BG,
    COLOR_CARD,
    COLOR_TEXT,
    DEFAULT_SAVE_DIR,
    WINDOW_GEOMETRY,
    WINDOW_MINSIZE,
)
from magoloader.version import __version__
from magoloader.core.analytics import Analytics
from magoloader.i18n import t
from magoloader.utils import ensure_dir
from magoloader.core.branding_settings import load_settings
from magoloader.ui.state import BrandingState, SaveDirState
from magoloader.ui.tabs import ProfileTab, UrlTab
from magoloader.ui.task_runner import TaskRunner

UI_QUEUE_POLL_MS = 200


class MagoLoaderApp(ctk.CTk):
    """Ventana principal. Cada flujo vive en su propia pestaña (magoloader/ui/tabs)."""

    def __init__(self):
        super().__init__()
        self.title(f"{t('app.title')} v{__version__}")
        self.geometry(WINDOW_GEOMETRY)
        self.minsize(*WINDOW_MINSIZE)

        # application icon
        try:
            icon_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "..", "..", "magoloader.ico"
            )
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except Exception:
            pass

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.configure(fg_color=COLOR_BG)

        # Servicios compartidos entre pestañas
        self.analytics = Analytics()
        self.analytics.track_app_start()
        self.runner = TaskRunner(queue.Queue(), self.analytics)
        self.save_dir_state = SaveDirState(DEFAULT_SAVE_DIR)
        self.branding_state = BrandingState(load_settings())

        self._build_ui()
        self._process_ui_queue()

    def _build_ui(self) -> None:
        ctk.CTkLabel(
            self,
            text=t("app.title"),
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=COLOR_TEXT,
        ).pack(anchor="w", padx=16, pady=(12, 0))

        self.tabview = ctk.CTkTabview(
            self,
            fg_color=COLOR_BG,
            segmented_button_fg_color=COLOR_CARD,
            segmented_button_selected_color=COLOR_ACCENT,
            segmented_button_selected_hover_color=COLOR_ACCENT_HOVER,
            segmented_button_unselected_color=COLOR_CARD,
            segmented_button_unselected_hover_color=COLOR_CARD,
            text_color=COLOR_TEXT,
            anchor="w",
        )
        self.tabview.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        services = {
            "runner": self.runner,
            "save_dir_state": self.save_dir_state,
            "analytics": self.analytics,
            "branding_state": self.branding_state,
        }
        tabs = [
            (t("tabs.profile"), ProfileTab),
            (t("tabs.url"), UrlTab),
        ]
        self.tabs = {}
        for name, tab_cls in tabs:
            container = self.tabview.add(name)
            tab = tab_cls(container, **services)
            tab.pack(fill="both", expand=True)
            self.tabs[name] = tab
        self.tabview.set(t("tabs.profile"))

    def _process_ui_queue(self) -> None:
        self.runner.process_pending()
        self.after(UI_QUEUE_POLL_MS, self._process_ui_queue)


def run_app():
    ensure_dir(DEFAULT_SAVE_DIR)

    # Mandatory version check before launching the main window
    from magoloader.core.updater import check_for_updates
    from magoloader.ui.update_dialog import UpdateDialog

    update_info = check_for_updates()
    if update_info.update_available:
        root = ctk.CTk()
        root.withdraw()
        UpdateDialog(root, update_info)
        root.mainloop()
        return  # user either downloaded or exited; never reached

    app = MagoLoaderApp()
    app.mainloop()
