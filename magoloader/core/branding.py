# -*- coding: utf-8 -*-
"""
Personalización de video: degradado inferior, logo y nombre como marca de agua.

El overlay se dibuja con Pillow a la resolución exacta del video y FFmpeg lo
compone encima (filtro `overlay`), sin redimensionar el video y copiando el audio.
"""

import os
import re
import tempfile
import threading
from dataclasses import dataclass
from typing import Callable, List, NamedTuple, Optional

from PIL import Image, ImageDraw, ImageFont

from magoloader.core.ffmpeg import get_ffmpeg_path, popen_hidden, run_hidden

# --------------------------------------------------------------------- diseño
# Proporciones relativas al tamaño del video (ajustables sin tocar la lógica).
GRADIENT_HEIGHT_RATIO = 0.35      # alto de la banda del degradado (fracción de H)
GRADIENT_MAX_ALPHA = 0.92         # opacidad en el borde inferior
PADDING_RATIO = 0.035             # padding (fracción de min(W, H))
LOGO_MAX_WIDTH_RATIO = 0.20       # caja máxima del logo (fracción de W)
LOGO_MAX_HEIGHT_RATIO = 0.12      # caja máxima del logo (fracción de H)
TEXT_SIZE_RATIO = 0.045           # tamaño de fuente inicial (fracción de min(W, H))
TEXT_MIN_SIZE = 10                # tamaño mínimo de fuente en px
TEXT_BOTTOM_PADDING_FACTOR = 1.6  # distancia del texto al borde inferior (x padding)
TEXT_COLOR = (255, 255, 255, 255)
SHADOW_COLOR = (0, 0, 0, 128)

# Fuentes en negrita a probar, en orden (Windows primero).
_BOLD_FONTS = ("arialbd.ttf", "segoeuib.ttf", "DejaVuSans-Bold.ttf")

LOGO_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")
_LOGO_FORMATS = {"PNG", "JPEG", "WEBP", "MPO"}

# Bytes finales de stderr de FFmpeg que se conservan para el mensaje de error.
_STDERR_TAIL_BYTES = 4096

_HEX_RE = re.compile(r"^#?([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")
_SIZE_RE = re.compile(r"\bVideo:.*?\b(\d{2,5})x(\d{2,5})\b")
_DURATION_RE = re.compile(r"Duration:\s*(\d+):(\d{2}):(\d{2}(?:\.\d+)?)")
_ROTATE_RE = re.compile(r"rotate\s*:\s*(-?\d+)")
_DISPLAYMATRIX_RE = re.compile(r"rotation of\s*(-?\d+(?:\.\d+)?)\s*degrees")


@dataclass(frozen=True)
class BrandingOptions:
    """Opciones de personalización ya validadas (instantánea inmutable)."""

    color: str
    logo_path: Optional[str] = None
    name: str = ""


class BrandingError(RuntimeError):
    """Fallo al personalizar; el video descargado sin personalizar sigue en `video_path`."""

    def __init__(self, message: str, video_path: str):
        super().__init__(message)
        self.video_path = video_path


class VideoInfo(NamedTuple):
    """Datos básicos de un video obtenidos con FFmpeg."""

    width: int
    height: int
    duration: float
    has_audio: bool


# ------------------------------------------------------------------ validación


def normalize_hex_color(text: Optional[str]) -> Optional[str]:
    """
    Normaliza un color HEX (`#RRGGBB`, `RRGGBB`, `#RGB`, `RGB`) a `#RRGGBB` en
    mayúsculas. Devuelve None si el texto no es un HEX válido.
    """
    if not text:
        return None
    match = _HEX_RE.match(text.strip())
    if not match:
        return None
    digits = match.group(1).upper()
    if len(digits) == 3:
        digits = "".join(c * 2 for c in digits)
    return f"#{digits}"


def hex_to_rgb(color: str) -> tuple:
    """Convierte `#RRGGBB` a una tupla (r, g, b)."""
    value = color.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def load_logo(path: str) -> Image.Image:
    """Abre un logo PNG/JPG/WEBP y lo devuelve en RGBA. Lanza ValueError si no es válido."""
    if not path or not os.path.isfile(path):
        raise ValueError(f"Logo not found: {path}")
    try:
        with Image.open(path) as img:
            if img.format not in _LOGO_FORMATS:
                raise ValueError(f"Unsupported logo format: {img.format}")
            img.load()
            return img.convert("RGBA")
    except ValueError:
        raise
    except Exception as exc:  # noqa: BLE001 - cualquier error de Pillow
        raise ValueError(f"Invalid logo image: {exc}") from exc


# -------------------------------------------------------------------- overlay


def _smoothstep(p: float) -> float:
    return p * p * (3.0 - 2.0 * p)


def _load_bold_font(size: int) -> ImageFont.ImageFont:
    for name in _BOLD_FONTS:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default(size=size)


def _draw_gradient(overlay: Image.Image, color: str) -> None:
    width, height = overlay.size
    band = max(1, round(height * GRADIENT_HEIGHT_RATIO))
    r, g, b = hex_to_rgb(color)
    column = Image.new("RGBA", (1, band))
    denom = max(1, band - 1)
    column.putdata([
        (r, g, b, round(255 * GRADIENT_MAX_ALPHA * _smoothstep(y / denom)))
        for y in range(band)
    ])
    overlay.paste(column.resize((width, band), Image.NEAREST), (0, height - band))


def _draw_logo(overlay: Image.Image, logo_path: str, pad: int) -> None:
    width, height = overlay.size
    logo = load_logo(logo_path)
    box_w = max(1, round(width * LOGO_MAX_WIDTH_RATIO))
    box_h = max(1, round(height * LOGO_MAX_HEIGHT_RATIO))
    scale = min(box_w / logo.width, box_h / logo.height)
    size = (max(1, round(logo.width * scale)), max(1, round(logo.height * scale)))
    logo = logo.resize(size, Image.LANCZOS)
    overlay.alpha_composite(logo, (width - pad - logo.width, pad))


def _draw_name(overlay: Image.Image, name: str, pad: int) -> None:
    width, height = overlay.size
    max_text_w = max(1, width - 2 * pad)
    size = max(TEXT_MIN_SIZE, round(min(width, height) * TEXT_SIZE_RATIO))
    font = _load_bold_font(size)
    probe = ImageDraw.Draw(overlay)
    while size > TEXT_MIN_SIZE and probe.textlength(name, font=font) > max_text_w:
        size -= 1
        font = _load_bold_font(size)
    # Con la fuente mínima y aún demasiado ancho: recortar con elipsis.
    if probe.textlength(name, font=font) > max_text_w:
        while len(name) > 1 and probe.textlength(name + "…", font=font) > max_text_w:
            name = name[:-1]
        name = name.rstrip() + "…"

    anchor_xy = (width / 2, height - TEXT_BOTTOM_PADDING_FACTOR * pad)
    offset = max(1, size // 18)
    layer = Image.new("RGBA", overlay.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.text(
        (anchor_xy[0] + offset, anchor_xy[1] + offset),
        name, font=font, fill=SHADOW_COLOR, anchor="md",
    )
    draw.text(anchor_xy, name, font=font, fill=TEXT_COLOR, anchor="md")
    overlay.alpha_composite(layer)


def render_overlay(width: int, height: int, options: BrandingOptions) -> Image.Image:
    """Genera el overlay RGBA transparente (degradado, logo y nombre) de tamaño W x H."""
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    pad = max(1, round(min(width, height) * PADDING_RATIO))
    _draw_gradient(overlay, options.color)
    if options.logo_path:
        _draw_logo(overlay, options.logo_path, pad)
    name = (options.name or "").strip()
    if name:
        _draw_name(overlay, name, pad)
    return overlay


# ---------------------------------------------------------------- FFmpeg


def parse_probe_output(stderr: str) -> VideoInfo:
    """Extrae tamaño (ya rotado), duración y presencia de audio de la salida de `ffmpeg -i`."""
    size = _SIZE_RE.search(stderr)
    if not size:
        raise ValueError("No video stream found")
    width, height = int(size.group(1)), int(size.group(2))

    rotation = 0.0
    rot = _ROTATE_RE.search(stderr)
    if rot:
        rotation = float(rot.group(1))
    else:
        matrix = _DISPLAYMATRIX_RE.search(stderr)
        if matrix:
            rotation = float(matrix.group(1))
    if round(abs(rotation)) % 180 == 90:
        width, height = height, width

    duration = 0.0
    dur = _DURATION_RE.search(stderr)
    if dur:
        h, m, s = dur.groups()
        duration = int(h) * 3600 + int(m) * 60 + float(s)

    has_audio = re.search(r"Stream #\d+:\d+.*?: Audio:", stderr) is not None
    return VideoInfo(width, height, duration, has_audio)


def probe_video(path: str) -> VideoInfo:
    """Obtiene tamaño, duración y audio de un video ejecutando `ffmpeg -i`."""
    result = run_hidden(
        [get_ffmpeg_path(), "-hide_banner", "-i", path],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return parse_probe_output(result.stderr or "")


def _build_command(
    ffmpeg: str, video_path: str, overlay_png: str, output: str, info: VideoInfo
) -> List[str]:
    odd = info.width % 2 or info.height % 2
    pix_fmt = "yuv444p" if odd else "yuv420p"
    cmd = [
        ffmpeg, "-hide_banner", "-nostdin", "-y",
        "-i", video_path,
        "-i", overlay_png,
        "-filter_complex", f"[0:v][1:v]overlay=0:0:format=auto,format={pix_fmt}[v]",
        "-map", "[v]",
        "-map", "0:a?",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
    ]
    if odd:
        cmd += ["-profile:v", "high444"]
    cmd += [
        "-c:a", "copy",
        "-movflags", "+faststart",
        "-progress", "pipe:1", "-nostats",
        output,
    ]
    return cmd


def _remove_quietly(path: Optional[str]) -> None:
    if path and os.path.exists(path):
        try:
            os.remove(path)
        except OSError:
            pass


def apply_branding(
    video_path: str,
    options: BrandingOptions,
    on_progress: Optional[Callable[[float], None]] = None,
) -> str:
    """
    Aplica el overlay al video y reemplaza el archivo. Devuelve la ruta final (.mp4).

    Si algo falla, el archivo original queda intacto, se eliminan los temporales
    y se lanza BrandingError. `on_progress` recibe fracciones 0..1 (desde el hilo
    de trabajo).
    """
    stem, ext = os.path.splitext(video_path)
    final_path = video_path if ext.lower() == ".mp4" else stem + ".mp4"
    tmp_output = stem + ".branding.tmp.mp4"
    overlay_png: Optional[str] = None
    try:
        ffmpeg = get_ffmpeg_path()
        info = probe_video(video_path)

        fd, overlay_png = tempfile.mkstemp(prefix="magoloader_overlay_", suffix=".png")
        os.close(fd)
        render_overlay(info.width, info.height, options).save(overlay_png, "PNG")

        cmd = _build_command(ffmpeg, video_path, overlay_png, tmp_output, info)
        progress = _ProgressTracker(on_progress)
        stderr_tail = _run_ffmpeg(cmd, info.duration, progress.report)
        if stderr_tail is not None:
            raise RuntimeError(stderr_tail.strip() or "FFmpeg failed")
        if not os.path.isfile(tmp_output) or os.path.getsize(tmp_output) == 0:
            raise RuntimeError("FFmpeg produced no output")

        os.replace(tmp_output, final_path)
        if final_path != video_path:
            _remove_quietly(video_path)
        progress.report(1.0)
        return final_path
    except BrandingError:
        raise
    except Exception as exc:  # noqa: BLE001 - se informa como fallo de personalización
        _remove_quietly(tmp_output)
        raise BrandingError(f"Branding failed: {exc}", video_path) from exc
    finally:
        _remove_quietly(overlay_png)


class _ProgressTracker:
    """Reenvía fracciones 0..1 al callback solo cuando aumentan."""

    def __init__(self, callback: Optional[Callable[[float], None]]):
        self._callback = callback
        self._last = 0.0

    def report(self, fraction: float) -> None:
        fraction = max(0.0, min(1.0, fraction))
        if self._callback is not None and fraction > self._last:
            self._last = fraction
            self._callback(fraction)


def _run_ffmpeg(
    cmd: List[str],
    duration: float,
    on_progress: Callable[[float], None],
) -> Optional[str]:
    """Ejecuta FFmpeg leyendo el progreso. Devuelve None si terminó bien o el final de stderr."""
    import subprocess

    proc = popen_hidden(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    tail: List[str] = []

    def drain_stderr() -> None:
        assert proc.stderr is not None
        for line in proc.stderr:
            tail.append(line)
            while sum(len(x) for x in tail) > _STDERR_TAIL_BYTES and len(tail) > 1:
                tail.pop(0)

    reader = threading.Thread(target=drain_stderr, daemon=True)
    with proc:
        reader.start()
        assert proc.stdout is not None
        for line in proc.stdout:
            key, _, value = line.strip().partition("=")
            if key in ("out_time_us", "out_time_ms") and duration > 0 and value.isdigit():
                # FFmpeg informa out_time_ms en microsegundos (igual que out_time_us).
                on_progress(int(value) / (duration * 1_000_000))
        code = proc.wait()
        reader.join(timeout=5)
    if code != 0:
        return "".join(tail) or f"FFmpeg exited with code {code}"
    return None
