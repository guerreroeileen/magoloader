# -*- coding: utf-8 -*-
"""Panel 'Personalización de video': color HEX, logo y nombre, sincronizado con BrandingState."""

import os
from tkinter import colorchooser, filedialog
from typing import List, Optional, Tuple

import customtkinter as ctk

from magoloader.constants import (
    COLOR_ACCENT,
    COLOR_ACCENT_HOVER,
    COLOR_CARD_DARK,
    COLOR_PLACEHOLDER,
    COLOR_TEXT,
    COLOR_TEXT_DIM,
    DEFAULT_BRANDING_COLOR,
)
from magoloader.core.branding import load_logo, normalize_hex_color
from magoloader.core.branding_settings import BrandingSettings, store_logo_copy
from magoloader.i18n import t
from magoloader.ui.state import BrandingState
from magoloader.ui.task_runner import TaskRunner

SAVE_DEBOUNCE_MS = 500
LOGO_PREVIEW_SIZE = 48


class BrandingPanel(ctk.CTkFrame):
    """
    Casilla 'Personalizar contenido' y, si está marcada, los campos de color, logo y nombre.

    Varios paneles (uno por pestaña) comparten el mismo BrandingState: cada edición
    actualiza el estado y los demás paneles se refrescan desde su suscripción.
    """

    def __init__(self, master, branding_state: BrandingState, runner: TaskRunner, **kwargs):
        super().__init__(
            master,
            fg_color=COLOR_CARD_DARK,
            border_color=COLOR_ACCENT,
            border_width=1,
            corner_radius=10,
            **kwargs,
        )
        self._state = branding_state
        self._runner = runner
        self._applying = False          # True mientras se aplican cambios externos
        self._save_job: Optional[str] = None
        self._swatch_color = DEFAULT_BRANDING_COLOR
        self._logo_image_ref: Optional[ctk.CTkImage] = None
        self._shown_logo: Optional[Tuple[str, float]] = None  # (ruta, mtime) mostrado

        self._build_ui()
        self._apply_settings(branding_state.get(), force_logo=True)
        self._on_lock_changed(branding_state.is_locked())
        branding_state.subscribe(self._on_settings_changed)
        branding_state.subscribe_lock(self._on_lock_changed)

    # -------------------------------------------------------------------- UI

    def _build_ui(self) -> None:
        ctk.CTkLabel(
            self,
            text=t("branding.title"),
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLOR_TEXT_DIM,
            anchor="w",
        ).pack(fill="x", padx=10, pady=(8, 2))

        self._enabled_var = ctk.BooleanVar(value=False)
        self.checkbox = ctk.CTkCheckBox(
            self,
            text=t("branding.enable"),
            variable=self._enabled_var,
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
            text_color=COLOR_TEXT,
            command=self._on_enabled_toggled,
        )
        self.checkbox.pack(anchor="w", padx=10, pady=(2, 8))

        self.body = ctk.CTkFrame(self, fg_color="transparent")

        # Color
        self._label(self.body, t("branding.color"))
        color_row = ctk.CTkFrame(self.body, fg_color="transparent")
        color_row.pack(fill="x", pady=(0, 8))
        self.swatch = ctk.CTkButton(
            color_row,
            text="",
            width=32,
            height=28,
            corner_radius=4,
            fg_color=self._swatch_color,
            hover_color=self._swatch_color,
            border_width=1,
            border_color=COLOR_TEXT_DIM,
            command=self._pick_color,
        )
        self.swatch.pack(side="left", padx=(0, 8))
        self._color_var = ctk.StringVar(value="")
        self.color_entry = ctk.CTkEntry(
            color_row, textvariable=self._color_var, height=28, border_color=COLOR_ACCENT
        )
        self.color_entry.pack(side="left", fill="x", expand=True)
        self._color_var.trace_add("write", lambda *_: self._on_color_edited())

        # Logo
        self._label(self.body, t("branding.logo"))
        logo_row = ctk.CTkFrame(self.body, fg_color="transparent")
        logo_row.pack(fill="x", pady=(0, 8))
        # La vista previa se empaqueta primero (a la derecha) para que no se comprima.
        self.logo_preview = ctk.CTkLabel(
            logo_row,
            text=t("branding.no_logo"),
            width=LOGO_PREVIEW_SIZE + 8,
            height=LOGO_PREVIEW_SIZE + 8,
            corner_radius=6,
            fg_color=COLOR_PLACEHOLDER,
            text_color=COLOR_TEXT_DIM,
            font=ctk.CTkFont(size=10),
            wraplength=LOGO_PREVIEW_SIZE,
        )
        self.logo_preview.pack(side="right", padx=(8, 0))
        buttons = ctk.CTkFrame(logo_row, fg_color="transparent")
        buttons.pack(side="left", fill="x", expand=True)
        self.logo_browse = ctk.CTkButton(
            buttons,
            text=t("sidebar.browse"),
            height=28,
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
            command=self._browse_logo,
        )
        self.logo_browse.pack(fill="x", pady=(0, 4))
        self.logo_remove = ctk.CTkButton(
            buttons,
            text=t("branding.logo_remove"),
            height=24,
            fg_color=COLOR_PLACEHOLDER,
            hover_color=COLOR_CARD_DARK,
            command=self._remove_logo,
        )
        self.logo_remove.pack(fill="x")

        # Nombre
        self._label(self.body, t("branding.name"))
        # Sin textvariable: CTkEntry ignora placeholder_text cuando tiene una variable.
        self.name_entry = ctk.CTkEntry(
            self.body,
            placeholder_text=t("branding.name_placeholder"),
            height=28,
            border_color=COLOR_ACCENT,
        )
        self.name_entry.pack(fill="x", pady=(0, 10))
        for event in ("<KeyRelease>", "<<Paste>>", "<<Cut>>", "<FocusOut>"):
            self.name_entry.bind(event, lambda _e: self.after_idle(self._on_name_edited), add="+")

    @staticmethod
    def _label(master, text: str) -> None:
        ctk.CTkLabel(
            master, text=text, font=ctk.CTkFont(size=12), text_color=COLOR_TEXT, anchor="w"
        ).pack(fill="x", pady=(0, 2))

    def _interactive_widgets(self) -> List[ctk.CTkBaseClass]:
        return [
            self.checkbox,
            self.swatch,
            self.color_entry,
            self.logo_browse,
            self.logo_remove,
            self.name_entry,
        ]

    # ----------------------------------------------------- estado → widgets

    def _on_settings_changed(self, settings: BrandingSettings) -> None:
        self._apply_settings(settings)

    def _apply_settings(self, settings: BrandingSettings, force_logo: bool = False) -> None:
        """Refleja los ajustes en los widgets sin disparar los handlers de edición."""
        self._applying = True
        try:
            if self._enabled_var.get() != settings.enabled:
                self._enabled_var.set(settings.enabled)
            if self._color_var.get() != settings.color_text:
                self._color_var.set(settings.color_text)
            self._set_name_text(settings.name)
            self._set_body_visible(settings.enabled)
            self._update_swatch(settings.color_text)
            self._show_logo(settings.logo_path, force=force_logo)
        finally:
            self._applying = False

    def _set_body_visible(self, visible: bool) -> None:
        if visible and not self.body.winfo_manager():
            self.body.pack(fill="x", padx=10)
        elif not visible and self.body.winfo_manager():
            self.body.pack_forget()

    def _update_swatch(self, color_text: str) -> None:
        color = normalize_hex_color(color_text)
        if color:
            self._swatch_color = color
        self.swatch.configure(fg_color=self._swatch_color, hover_color=self._swatch_color)

    def _show_logo(self, logo_path: Optional[str], force: bool = False) -> None:
        """Actualiza la miniatura solo si cambió el archivo (ruta o fecha de modificación)."""
        key = None
        if logo_path:
            try:
                key = (logo_path, os.path.getmtime(logo_path))
            except OSError:
                key = None
        if key == self._shown_logo and not force:
            return
        self._shown_logo = key
        image = None
        if key is not None:
            try:
                logo = load_logo(logo_path)
                logo.thumbnail((LOGO_PREVIEW_SIZE, LOGO_PREVIEW_SIZE))
                image = ctk.CTkImage(light_image=logo, dark_image=logo, size=logo.size)
            except ValueError:
                image = None
        if image is not None:
            self.logo_preview.configure(image=image, text="", fg_color="transparent")
        else:
            # CTkLabel no limpia la imagen interna con image=None; si no se quita a mano,
            # Tk intenta redibujar una imagen ya liberada ("pyimage doesn't exist").
            self.logo_preview._label.configure(image="")
            self.logo_preview.configure(
                image=None, text=t("branding.no_logo"), fg_color=COLOR_PLACEHOLDER
            )
        # Soltar la referencia anterior solo después de reconfigurar el label.
        self._logo_image_ref = image

    def _on_lock_changed(self, locked: bool) -> None:
        state = "disabled" if locked else "normal"
        for widget in self._interactive_widgets():
            widget.configure(state=state)

    # ----------------------------------------------------- widgets → estado

    def _on_enabled_toggled(self) -> None:
        if self._applying:
            return
        self._flush_pending_save()
        self._state.update(enabled=bool(self._enabled_var.get()))

    def _on_color_edited(self) -> None:
        if self._applying:
            return
        text = self._color_var.get()
        self._update_swatch(text)
        self._state.update(color_text=text, persist=False)
        self._schedule_save()

    def _on_name_edited(self) -> None:
        if self._applying:
            return
        name = self.name_entry.get()  # devuelve "" mientras se muestra el placeholder
        if name == self._state.get().name:
            return
        self._state.update(name=name, persist=False)
        self._schedule_save()

    def _set_name_text(self, name: str) -> None:
        """Escribe el nombre en el campo sin perder el placeholder cuando queda vacío."""
        if self.name_entry.get() == name:
            return
        self.name_entry.delete(0, "end")
        if name:
            self.name_entry.insert(0, name)
        elif self.focus_get() is not self.name_entry._entry:
            self.name_entry._activate_placeholder()

    def _pick_color(self) -> None:
        _rgb, chosen = colorchooser.askcolor(
            color=self._swatch_color, title=t("branding.pick_color"), parent=self
        )
        if chosen:
            self._color_var.set(chosen.upper())  # dispara _on_color_edited

    def _browse_logo(self) -> None:
        path = filedialog.askopenfilename(
            parent=self,
            title=t("branding.logo_dialog"),
            filetypes=[(t("branding.image_files"), "*.png *.jpg *.jpeg *.webp")],
        )
        if not path:
            return
        try:
            stored = store_logo_copy(path)
        except (ValueError, OSError):
            self._runner.show_error(t("error.invalid_logo"))
            return
        # La copia siempre usa la misma ruta: forzar la notificación para refrescar vistas.
        self._state.update(logo_path=stored, force=True)

    def _remove_logo(self) -> None:
        self._state.update(logo_path=None)

    # ------------------------------------------------------- guardado diferido

    def _schedule_save(self) -> None:
        if self._save_job is not None:
            self.after_cancel(self._save_job)
        self._save_job = self.after(SAVE_DEBOUNCE_MS, self._flush_pending_save)

    def _flush_pending_save(self) -> None:
        if self._save_job is not None:
            self.after_cancel(self._save_job)
            self._save_job = None
            self._state.save()

    def destroy(self) -> None:
        self._flush_pending_save()
        super().destroy()
