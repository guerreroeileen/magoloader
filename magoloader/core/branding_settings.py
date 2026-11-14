# -*- coding: utf-8 -*-
"""Ajustes de personalización de video: modelo, carga y guardado en JSON."""

import json
import os
from dataclasses import asdict, dataclass
from typing import Optional

from magoloader.constants import BRANDING_FILE, BRANDING_LOGO_FILE, DEFAULT_BRANDING_COLOR
from magoloader.core.branding import BrandingOptions, load_logo, normalize_hex_color


@dataclass(frozen=True)
class BrandingSettings:
    """
    Ajustes tal como los edita el usuario.

    `color_text` guarda el texto escrito (aunque sea inválido) para mostrarlo igual.
    """

    enabled: bool = False
    color_text: str = DEFAULT_BRANDING_COLOR
    logo_path: Optional[str] = None
    name: str = ""

    def to_options(self) -> Optional[BrandingOptions]:
        """
        Devuelve las opciones validadas, o None si la personalización está desactivada.
        Lanza ValueError si está activada y el color no es un HEX válido.
        """
        if not self.enabled:
            return None
        color = normalize_hex_color(self.color_text)
        if color is None:
            raise ValueError(f"Invalid HEX color: {self.color_text!r}")
        logo = self.logo_path if self.logo_path and os.path.isfile(self.logo_path) else None
        return BrandingOptions(color=color, logo_path=logo, name=self.name.strip())


def load_settings(path: str = BRANDING_FILE) -> BrandingSettings:
    """Carga los ajustes. Nunca lanza: los valores inválidos o ausentes usan el valor por defecto."""
    defaults = BrandingSettings()
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return defaults
    if not isinstance(data, dict):
        return defaults

    enabled = data.get("enabled")
    color_text = data.get("color_text")
    logo_path = data.get("logo_path")
    name = data.get("name")
    return BrandingSettings(
        enabled=enabled if isinstance(enabled, bool) else defaults.enabled,
        color_text=color_text if isinstance(color_text, str) else defaults.color_text,
        logo_path=logo_path if isinstance(logo_path, str) and os.path.isfile(logo_path) else None,
        name=name if isinstance(name, str) else defaults.name,
    )


def save_settings(settings: BrandingSettings, path: str = BRANDING_FILE) -> None:
    """Guarda los ajustes de forma atómica (archivo temporal + reemplazo)."""
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(asdict(settings), fh, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def store_logo_copy(src: str, dest: str = BRANDING_LOGO_FILE) -> str:
    """
    Valida el logo y guarda una copia PNG propia de la aplicación.
    Devuelve la ruta de la copia. Lanza ValueError si la imagen no es válida.
    """
    logo = load_logo(src)
    folder = os.path.dirname(dest)
    if folder:
        os.makedirs(folder, exist_ok=True)
    tmp = dest + ".tmp.png"
    logo.save(tmp, "PNG")
    os.replace(tmp, dest)
    return dest
