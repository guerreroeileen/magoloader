# -*- coding: utf-8 -*-
"""Ventana principal de MagoLoader."""

import queue
import threading
from typing import List

import customtkinter as ctk
from tkinter import messagebox, filedialog

from magoloader.constants import (
    COLOR_ACCENT,
    COLOR_BG,
    COLOR_CARD,
    DEFAULT_SAVE_DIR,
    VIDEOS_PER_PAGE,
    WINDOW_GEOMETRY,
    WINDOW_MINSIZE,
    WINDOW_TITLE,
)
from magoloader.core.downloader import download_video
from magoloader.core.extractors.factory import ExtractorFactory
from magoloader.core.models import ProfileInfo, VideoEntry
from magoloader.i18n import t
from magoloader.utils import (
    ensure_dir,
    is_ytdlp_extraction_error,
    is_ytdlp_ssl_error,
)
from magoloader.ui.components.header import Header
from magoloader.ui.components.sidebar import Sidebar
from magoloader.ui.components.footer import Footer
from magoloader.ui.components.pagination import PaginationBar
from magoloader.ui.components.video_card import VideoCard
from magoloader.ui.thumbnail_loader import load_thumbnail_async


def _entry_to_dict(e: VideoEntry) -> dict:
    """Convierte VideoEntry a dict para la UI (incluye thumbnail)."""
    return {
        "url": e.url,
        "id": e.id,
        "title": e.title or None,
        "duration": e.duration,
        "thumbnail": e.thumbnail,
    }


class MagoLoaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(t("app.title"))
        self.geometry(WINDOW_GEOMETRY)
        self.minsize(*WINDOW_MINSIZE)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.configure(fg_color=COLOR_BG)

        self.save_dir = DEFAULT_SAVE_DIR
        ensure_dir(self.save_dir)

        self.profile_info: ProfileInfo | None = None
        self.video_entries: List[dict] = []
        self.selected_urls: set = set()
        self.current_page = 0
        self.pending_ui_updates: queue.Queue = queue.Queue()
        self._analysis_running = False
        self._download_running = False

        self._build_ui()
        self._process_ui_queue()

    def _build_ui(self):
        # Header
        self.header = Header(self, on_analyze=self._on_analyze)
        self.header.pack(fill="x", padx=16, pady=12)

        # Main: sidebar + center
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        self.sidebar = Sidebar(
            main,
            save_dir=self.save_dir,
            on_browse=self._browse_folder,
        )
        self.sidebar.pack(side="left", fill="y", padx=(0, 16))

        center = ctk.CTkFrame(main, fg_color="transparent")
        center.pack(side="left", fill="both", expand=True)

        # Top bar: select all
        top_bar = ctk.CTkFrame(center, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 8))

        ctk.CTkButton(
            top_bar,
            text=t("videos.select_page"),
            fg_color=COLOR_ACCENT,
            hover_color="#cc2444",
            command=self._select_all_current_page,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            top_bar,
            text=t("videos.select_all"),
            fg_color=COLOR_ACCENT,
            hover_color="#cc2444",
            command=self._select_all_videos,
        ).pack(side="left")

        self.scroll_videos = ctk.CTkScrollableFrame(
            center,
            fg_color=COLOR_CARD,
            corner_radius=12,
            scrollbar_button_color=COLOR_ACCENT,
        )
        self.scroll_videos.pack(fill="both", expand=True)

        self.videos_inner = ctk.CTkFrame(self.scroll_videos, fg_color="transparent")
        self.videos_inner.pack(fill="both", expand=True)

        self.pagination = PaginationBar(
            center,
            on_prev=self._prev_page,
            on_next=self._next_page,
        )
        self.pagination.pack(fill="x", pady=(8, 0))

        self.footer = Footer(self, on_download=self._on_download)
        self.footer.pack(fill="x", padx=16, pady=12)

    def _process_ui_queue(self):
        try:
            while True:
                callback = self.pending_ui_updates.get_nowait()
                if callable(callback):
                    callback()
        except queue.Empty:
            pass
        self.after(200, self._process_ui_queue)

    def _run_in_thread(self, target, on_done=None):
        def wrapper():
            try:
                target()
            except Exception as e:
                if is_ytdlp_ssl_error(e):
                    self.pending_ui_updates.put(
                        lambda: self._show_error(t("error.ytdlp_ssl"))
                    )
                elif is_ytdlp_extraction_error(e):
                    self.pending_ui_updates.put(
                        lambda: self._show_error(t("error.ytdlp"))
                    )
                else:
                    self.pending_ui_updates.put(
                        lambda err=e: self._show_error(str(err) or repr(err))
                    )
            finally:
                if on_done:
                    self.pending_ui_updates.put(on_done)

        threading.Thread(target=wrapper, daemon=True).start()

    def _show_error(self, msg: str):
        messagebox.showerror("Error", msg)

    def _show_info(self, msg: str):
        messagebox.showinfo(t("app.title"), msg)

    def _on_analyze(self):
        raw = self.header.get_username()
        if not raw:
            self._show_error(t("error.no_username"))
            return
        username = raw.lstrip("@")
        if self._analysis_running:
            return
        self._analysis_running = True
        self.header.set_analyzing(True)

        def do_analyze():
            extractor = ExtractorFactory.get_extractor(username)
            profile = extractor.extract(username)
            self.profile_info = profile
            self.pending_ui_updates.put(self._apply_profile_and_videos)

        def on_done():
            self._analysis_running = False
            self.header.set_analyzing(False)

        self._run_in_thread(do_analyze, on_done)

    def _apply_profile_and_videos(self):
        if not self.profile_info:
            return
        info = self.profile_info
        self.sidebar.set_profile(
            info.uploader,
            info.username,
            len(info.entries),
        )
        self.video_entries = [_entry_to_dict(e) for e in info.entries]
        self.selected_urls = {e["url"] for e in self.video_entries}
        self.current_page = 0
        self._render_page()
        self._update_pagination_ui()
        self._update_download_button_label()
        # Cargar avatar del perfil en segundo plano
        if info.thumbnail:
            load_thumbnail_async(
                info.thumbnail,
                lambda path: self.pending_ui_updates.put(
                    lambda p=path: self.sidebar.set_profile_avatar(p)
                ),
            )

    def _get_current_page_entries(self) -> List[dict]:
        start = self.current_page * VIDEOS_PER_PAGE
        return self.video_entries[start : start + VIDEOS_PER_PAGE]

    def _total_pages(self) -> int:
        if not self.video_entries:
            return 1
        return (len(self.video_entries) + VIDEOS_PER_PAGE - 1) // VIDEOS_PER_PAGE

    def _render_page(self):
        for w in self.videos_inner.winfo_children():
            w.destroy()

        page_entries = self._get_current_page_entries()
        row, col = 0, 0
        for entry in page_entries:
            var = ctk.BooleanVar(value=entry["url"] in self.selected_urls)
            on_toggle = lambda u=entry["url"], v=var: self._sync_selection(u, v)
            card = VideoCard(
                self.videos_inner,
                entry=entry,
                var=var,
                on_toggle=on_toggle,
                ui_update_queue=self.pending_ui_updates,
            )
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            col += 1
            if col >= 2:
                col = 0
                row += 1

        self.videos_inner.columnconfigure(0, weight=1)
        self.videos_inner.columnconfigure(1, weight=1)

    def _sync_selection(self, url: str, var: ctk.BooleanVar):
        if var.get():
            self.selected_urls.add(url)
        else:
            self.selected_urls.discard(url)
        self._update_download_button_label()

    def _update_pagination_ui(self):
        total = self._total_pages()
        self.pagination.update_state(self.current_page, total)

    def _prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self._render_page()
            self._update_pagination_ui()

    def _next_page(self):
        total = self._total_pages()
        if self.current_page < total - 1:
            self.current_page += 1
            self._render_page()
            self._update_pagination_ui()

    def _select_all_current_page(self):
        page_entries = self._get_current_page_entries()
        urls_on_page = {e["url"] for e in page_entries}
        if not urls_on_page:
            return
        if urls_on_page <= self.selected_urls:
            self.selected_urls -= urls_on_page
        else:
            self.selected_urls |= urls_on_page
        self._render_page()
        self._update_download_button_label()

    def _select_all_videos(self):
        if not self.video_entries:
            return
        all_urls = {e["url"] for e in self.video_entries}
        if all_urls == self.selected_urls:
            self.selected_urls.clear()
        else:
            self.selected_urls = set(all_urls)
        self._render_page()
        self._update_download_button_label()

    def _update_download_button_label(self):
        self.footer.set_download_label(len(self.selected_urls))

    def _browse_folder(self):
        path = filedialog.askdirectory(
            initialdir=self.save_dir,
            title=t("sidebar.save_location"),
        )
        if path:
            self.save_dir = path
            ensure_dir(self.save_dir)
            self.sidebar.set_save_dir(self.save_dir)

    def _on_download(self):
        selected = [
            e for e in self.video_entries if e["url"] in self.selected_urls
        ]
        if not selected:
            self._show_error(t("error.no_videos_selected"))
            return
        if self._download_running:
            return
        self._download_running = True
        self.footer.set_download_enabled(False)
        self.footer.set_progress(0)

        total = len(selected)

        def do_download():
            for i, entry in enumerate(selected):
                try:
                    download_video(entry["url"], self.save_dir)
                except Exception:
                    pass
                pct = (i + 1) / total
                self.pending_ui_updates.put(
                    lambda p=pct: self.footer.set_progress(p)
                )

        def on_done():
            self._download_running = False
            self.footer.set_download_enabled(True)
            self._show_info(t("info.download_finished"))

        self._run_in_thread(do_download, on_done)


def run_app():
    ensure_dir(DEFAULT_SAVE_DIR)
    app = MagoLoaderApp()
    app.mainloop()
