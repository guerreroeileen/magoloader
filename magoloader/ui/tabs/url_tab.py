# -*- coding: utf-8 -*-
"""Pestaña URL de video: vista previa y descarga de un único video de TikTok."""

from typing import Optional

import customtkinter as ctk

from magoloader.constants import COLOR_CARD, COLOR_TEXT_DIM
from magoloader.core.analytics import Analytics
from magoloader.core.branding import BrandingError
from magoloader.core.downloader import STAGE_BRANDING, download_video
from magoloader.core.extractors.factory import ExtractorFactory
from magoloader.core.models import VideoEntry
from magoloader.i18n import t
from magoloader.ui.components.branding_panel import BrandingPanel
from magoloader.ui.components.footer import Footer
from magoloader.ui.components.input_bar import InputBar
from magoloader.ui.components.save_folder_picker import SaveFolderPicker
from magoloader.ui.components.video_card import VideoCard
from magoloader.ui.state import BrandingState, SaveDirState
from magoloader.ui.task_runner import TaskRunner
from magoloader.utils import is_ytdlp_extraction_error, normalize_tiktok_video_url

# Fragmentos de error de yt-dlp que indican un video no disponible (privado,
# eliminado, publicación de imágenes sin formato de video, etc.).
_UNAVAILABLE_HINTS = (
    "no video formats found",
    "video unavailable",
    "this video is unavailable",
    "not available",
    "private",
    "removed",
    "deleted",
    "status code 10204",
    "unable to find video",
    "único video",
)


def _map_url_error(exc: Exception) -> str:
    """Mensaje traducido para errores al obtener/descargar un video por URL."""
    msg = str(exc).lower()
    if any(hint in msg for hint in _UNAVAILABLE_HINTS):
        return t("error.video_unavailable")
    if is_ytdlp_extraction_error(exc):
        return t("err_ytdlp_outdated")
    return t("error.video_unavailable")


class UrlTab(ctk.CTkFrame):
    """
    Estados: idle → fetching → ready → downloading → ready.
    Editar la URL en `ready` vuelve a `idle` (desactiva Descargar).
    """

    def __init__(
        self,
        master,
        runner: TaskRunner,
        save_dir_state: SaveDirState,
        analytics: Analytics,
        branding_state: BrandingState,
        **kwargs,
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.runner = runner
        self.save_dir_state = save_dir_state
        self.analytics = analytics
        self.branding_state = branding_state

        self._entry: Optional[VideoEntry] = None
        self._fetched_input: Optional[str] = None
        self._pending_input: Optional[str] = None
        self._fetch_running = False
        self._download_running = False
        self._preview_card: Optional[VideoCard] = None

        self._build_ui()
        self._refresh_controls()

    def _build_ui(self) -> None:
        self.input_bar = InputBar(
            self,
            placeholder=t("url.placeholder"),
            button_text=t("url.fetch"),
            busy_text=t("url.fetching"),
            on_submit=self._on_fetch,
        )
        self.input_bar.pack(fill="x", pady=(0, 12))
        self.input_bar.bind_change(self._on_url_changed)

        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, pady=(0, 12))

        side = ctk.CTkFrame(main, width=260, fg_color=COLOR_CARD, corner_radius=12)
        side.pack(side="left", fill="y", padx=(0, 16))
        side.pack_propagate(False)
        side_body = ctk.CTkScrollableFrame(side, fg_color=COLOR_CARD, corner_radius=12)
        side_body.pack(fill="both", expand=True)
        SaveFolderPicker(side_body, save_dir_state=self.save_dir_state).pack(
            fill="x", padx=12, pady=(8, 0)
        )
        BrandingPanel(side_body, branding_state=self.branding_state, runner=self.runner).pack(
            fill="x", padx=8, pady=(0, 12)
        )

        self.preview_area = ctk.CTkFrame(main, fg_color=COLOR_CARD, corner_radius=12)
        self.preview_area.pack(side="left", fill="both", expand=True)

        self.hint_label = ctk.CTkLabel(
            self.preview_area,
            text=t("url.empty_hint"),
            font=ctk.CTkFont(size=14),
            text_color=COLOR_TEXT_DIM,
            wraplength=420,
            justify="center",
        )
        self.hint_label.place(relx=0.5, rely=0.5, anchor="center")

        self.footer = Footer(self, on_download=self._on_download, button_text=t("url.download"))
        self.footer.pack(fill="x")

    # ----------------------------------------------------------------- estado

    def _refresh_controls(self) -> None:
        """Sincroniza botones con el estado actual (llamar en el hilo UI)."""
        busy = self._fetch_running or self._download_running
        if self._fetch_running:
            self.input_bar.set_busy(True)
        else:
            self.input_bar.set_busy(False)
            self.input_bar.set_enabled(not self._download_running)
        self.footer.set_download_enabled(self._entry is not None and not busy)

    def _show_preview(self, entry: VideoEntry) -> None:
        self._clear_preview()
        self.hint_label.place_forget()
        card_data = {
            "url": entry.url,
            "id": entry.id,
            "title": entry.title,
            "duration": entry.duration,
            "thumbnail": entry.thumbnail,
        }
        self._preview_card = VideoCard(
            self.preview_area,
            entry=card_data,
            var=None,
            on_toggle=None,
            ui_update_queue=self.runner.queue,
            selectable=False,
        )
        self._preview_card.place(relx=0.5, rely=0.5, anchor="center")

    def _clear_preview(self) -> None:
        if self._preview_card is not None:
            self._preview_card.destroy()
            self._preview_card = None
        self.hint_label.place(relx=0.5, rely=0.5, anchor="center")

    def _on_url_changed(self) -> None:
        """Editar la URL invalida la vista previa (excepto durante la descarga)."""
        if self._download_running or self._entry is None:
            return
        if self.input_bar.get_value() != self._fetched_input:
            self._entry = None
            self._fetched_input = None
            self._clear_preview()
            self.footer.set_progress(0)
            self._refresh_controls()

    # ------------------------------------------------------------------ fetch

    def _on_fetch(self) -> None:
        if self._fetch_running or self._download_running:
            return
        raw = self.input_bar.get_value()
        if not raw:
            self.runner.show_error(t("error.no_url"))
            return
        url = normalize_tiktok_video_url(raw)
        if url is None:
            self.runner.show_error(t("error.invalid_url"))
            return

        self._fetch_running = True
        self._pending_input = raw
        self._entry = None
        self._fetched_input = None
        self._clear_preview()
        self.footer.set_progress(0)
        self._refresh_controls()

        def do_fetch() -> None:
            entry = ExtractorFactory.get_extractor(url).extract_video(url)
            self.runner.post(lambda e=entry, r=raw: self._apply_fetch_result(r, e))

        def on_done() -> None:
            self._fetch_running = False
            self._refresh_controls()

        self.runner.run(do_fetch, on_done, error_message=_map_url_error)

    def _apply_fetch_result(self, requested_input: str, entry: VideoEntry) -> None:
        # Ignorar resultados obsoletos si el usuario cambió la URL mientras tanto
        if requested_input != self.input_bar.get_value():
            return
        self._entry = entry
        self._fetched_input = requested_input
        self._show_preview(entry)

    # --------------------------------------------------------------- download

    def _on_download(self) -> None:
        if self._entry is None or self._fetch_running or self._download_running:
            return
        try:
            branding = self.branding_state.get().to_options()
        except ValueError:
            self.runner.show_error(t("error.invalid_hex"))
            return
        entry = self._entry
        save_dir = self.save_dir_state.get()

        self._download_running = True
        self.branding_state.set_locked(True)
        self.footer.set_progress(0)
        self.footer.set_button_text(t("url.downloading"))
        self._refresh_controls()

        def on_progress(fraction: float) -> None:
            self.runner.post(lambda p=fraction: self.footer.set_progress(p))

        def on_stage(stage: str) -> None:
            if stage == STAGE_BRANDING:
                self.runner.post(lambda: self.footer.set_button_text(t("branding.applying")))

        def do_download() -> None:
            try:
                path = download_video(
                    entry.url,
                    save_dir,
                    on_progress=on_progress,
                    branding=branding,
                    on_stage=on_stage,
                )
            except BrandingError as exc:
                # La descarga sí terminó: se informa que quedó sin personalizar.
                self.analytics.track_url_download()
                self.runner.post(lambda p=exc.video_path: self._on_branding_failed(p))
                return
            self.analytics.track_url_download()
            self.runner.post(lambda p=path: self._on_download_success(p, save_dir))

        def on_done() -> None:
            self._download_running = False
            self.branding_state.set_locked(False)
            self.footer.set_button_text(t("url.download"))
            self._refresh_controls()

        self.runner.run(do_download, on_done, error_message=_map_url_error)

    def _on_branding_failed(self, path: str) -> None:
        self.footer.set_progress(1.0)
        self.runner.show_info(t("info.saved_unbranded", path=path))

    def _on_download_success(self, path: Optional[str], save_dir: str) -> None:
        self.footer.set_progress(1.0)
        self.runner.show_info(t("url.saved_to", path=path or save_dir))
