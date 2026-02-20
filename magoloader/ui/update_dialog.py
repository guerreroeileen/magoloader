# -*- coding: utf-8 -*-
"""Modal dialog shown when a mandatory update is available."""

import os
import sys
import webbrowser

import customtkinter as ctk

from magoloader.constants import COLOR_BG, COLOR_ACCENT, COLOR_ACCENT_HOVER, COLOR_TEXT, COLOR_TEXT_DIM
from magoloader.i18n.translations import t
from magoloader.version import __version__


class UpdateDialog(ctk.CTkToplevel):
    """A modal, non-closable dialog that forces the user to update or exit.

    Parameters
    ----------
    parent : ctk.CTk
        The hidden root window.
    update_info : UpdateInfo
        Namedtuple with ``latest_version`` and ``download_url``.
    """

    def __init__(self, parent, update_info):
        super().__init__(parent)
        self._parent = parent
        self._update_info = update_info

        # Window setup
        self.title(t("update.title"))
        self.geometry("460x220")
        self.resizable(False, False)
        self.configure(fg_color=COLOR_BG)

        # Application icon
        try:
            icon_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "..", "..", "magoloader.ico"
            )
            if os.path.exists(icon_path):
                self.after(200, lambda: self.iconbitmap(icon_path))
        except Exception:
            pass

        # Prevent closing via the X button
        self.protocol("WM_DELETE_WINDOW", self._on_exit)

        # Center the dialog on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 460) // 2
        y = (self.winfo_screenheight() - 220) // 2
        self.geometry(f"460x220+{x}+{y}")

        # Make modal
        self.transient(parent)
        self.grab_set()

        self._build_ui()

    def _build_ui(self):
        """Build the dialog widgets."""
        # Icon / emoji header
        header = ctk.CTkLabel(
            self,
            text="🔄",
            font=ctk.CTkFont(size=36),
            text_color=COLOR_TEXT,
        )
        header.pack(pady=(18, 4))

        # Message body
        message = t(
            "update.message",
            current=__version__,
            latest=self._update_info.latest_version,
        )
        body = ctk.CTkLabel(
            self,
            text=message,
            font=ctk.CTkFont(size=13),
            text_color=COLOR_TEXT_DIM,
            wraplength=400,
            justify="center",
        )
        body.pack(pady=(0, 18))

        # Button row
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=(0, 14))

        download_btn = ctk.CTkButton(
            btn_frame,
            text=t("update.download"),
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
            width=160,
            height=38,
            command=self._on_download,
        )
        download_btn.pack(side="left", padx=10)

        exit_btn = ctk.CTkButton(
            btn_frame,
            text=t("update.exit"),
            font=ctk.CTkFont(size=14),
            fg_color="#333333",
            hover_color="#444444",
            width=120,
            height=38,
            command=self._on_exit,
        )
        exit_btn.pack(side="left", padx=10)

    def _on_download(self):
        """Open the release page in the default browser and exit."""
        webbrowser.open(self._update_info.download_url)
        self._shutdown()

    def _on_exit(self):
        """Close the application immediately."""
        self._shutdown()

    def _shutdown(self):
        """Destroy windows and terminate the process."""
        try:
            self.grab_release()
            self.destroy()
            self._parent.destroy()
        except Exception:
            pass
        sys.exit(0)
