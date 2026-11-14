# -*- coding: utf-8 -*-
"""Tests de la personalización de video (validación, overlay, FFmpeg, ajustes)."""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image  # noqa: E402

from magoloader.core.branding_settings import (  # noqa: E402
    BrandingSettings,
    load_settings,
    save_settings,
    store_logo_copy,
)
from magoloader.core.branding import (  # noqa: E402
    PADDING_RATIO,
    BrandingError,
    BrandingOptions,
    apply_branding,
    load_logo,
    normalize_hex_color,
    parse_probe_output,
    probe_video,
    render_overlay,
)


def _ffmpeg_path() -> Optional[str]:
    try:
        from magoloader.core.ffmpeg import get_ffmpeg_path

        return get_ffmpeg_path()
    except Exception:  # noqa: BLE001
        return None


FFMPEG = _ffmpeg_path()


def _make_logo(path: str, size: tuple = (200, 200)) -> None:
    """Logo circular azul con fondo transparente."""
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    from PIL import ImageDraw

    ImageDraw.Draw(img).ellipse((0, 0, size[0] - 1, size[1] - 1), fill=(10, 60, 200, 255))
    img.save(path, "PNG")


def _make_clip(path: str, width: int, height: int, audio: bool = True) -> None:
    """Genera un clip de prueba de 2 s con FFmpeg (testsrc + tono opcional)."""
    from magoloader.core.ffmpeg import run_hidden

    cmd = [
        FFMPEG, "-hide_banner", "-y",
        "-f", "lavfi", "-i", f"testsrc=size={width}x{height}:rate=30:duration=2",
    ]
    if audio:
        cmd += ["-f", "lavfi", "-i", "sine=frequency=440:duration=2", "-c:a", "aac"]
    cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-shortest", path]
    result = run_hidden(cmd, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode(errors="replace"))


class TestHexColor(unittest.TestCase):
    def test_valid_colors(self) -> None:
        self.assertEqual(normalize_hex_color("#0000ff"), "#0000FF")
        self.assertEqual(normalize_hex_color("0000FF"), "#0000FF")
        self.assertEqual(normalize_hex_color(" #0af "), "#00AAFF")
        self.assertEqual(normalize_hex_color("0af"), "#00AAFF")

    def test_invalid_colors(self) -> None:
        for text in ("", "#12345", "#GGGGGG", "blue", None, "#"):
            self.assertIsNone(normalize_hex_color(text), text)


class TestLoadLogo(unittest.TestCase):
    def test_png_with_alpha(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "logo.png")
            _make_logo(path)
            logo = load_logo(path)
            self.assertEqual(logo.mode, "RGBA")
            self.assertEqual(logo.getpixel((0, 0))[3], 0)
            self.assertEqual(logo.getpixel((100, 100))[3], 255)

    def test_not_an_image(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "fake.png")
            Path(path).write_text("not an image", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_logo(path)

    def test_missing_file(self) -> None:
        with self.assertRaises(ValueError):
            load_logo("does-not-exist.png")


class TestRenderOverlay(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.logo = os.path.join(self._tmp.name, "logo.png")
        _make_logo(self.logo)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _check(self, width: int, height: int) -> None:
        opts = BrandingOptions(color="#0000FF", logo_path=self.logo, name="@CaliEsCali_Oficial")
        img = render_overlay(width, height, opts)
        self.assertEqual(img.size, (width, height))
        self.assertEqual(img.mode, "RGBA")

        # Arriba a la izquierda: transparente
        self.assertEqual(img.getpixel((5, 5))[3], 0)
        # Mitad del video: fuera de la banda del degradado
        self.assertEqual(img.getpixel((5, height // 2))[3], 0)
        # Borde inferior: color elegido casi opaco
        r, g, b, a = img.getpixel((5, height - 1))
        self.assertEqual((r, g, b), (0, 0, 255))
        self.assertGreaterEqual(a, 200)

        # Degradado creciente en la columna izquierda (sin texto)
        alphas = [img.getpixel((2, y))[3] for y in range(height // 2, height)]
        self.assertEqual(alphas, sorted(alphas))

        # Logo arriba a la derecha, con padding transparente a la derecha y arriba
        pad = max(1, round(min(width, height) * PADDING_RATIO))
        logo_box = round(min(width * 0.20, height * 0.12))
        center = (width - pad - logo_box // 2, pad + logo_box // 2)
        self.assertGreater(img.getpixel(center)[3], 0)
        self.assertEqual(img.getpixel((width - 1, center[1]))[3], 0)
        self.assertEqual(img.getpixel((center[0], 0))[3], 0)

    def test_portrait(self) -> None:
        self._check(720, 1280)

    def test_landscape(self) -> None:
        self._check(1280, 720)

    def test_long_name_fits(self) -> None:
        width, height = 360, 640
        opts = BrandingOptions(color="#000000", name="@" + "MuyLargoNombre" * 10)
        img = render_overlay(width, height, opts)
        pad = max(1, round(min(width, height) * PADDING_RATIO))
        # Los márgenes laterales no tienen píxeles blancos del texto
        for y in range(height - height // 5, height):
            for x in list(range(0, pad - 2)) + list(range(width - pad + 2, width)):
                r, g, b, _ = img.getpixel((x, y))
                self.assertFalse(r > 200 and g > 200 and b > 200, (x, y))

    def test_gradient_only(self) -> None:
        img = render_overlay(100, 200, BrandingOptions(color="#FF0000"))
        self.assertEqual(img.getpixel((50, 199))[:3], (255, 0, 0))
        self.assertEqual(img.getpixel((95, 5))[3], 0)


class TestProbeParsing(unittest.TestCase):
    PLAIN = (
        "Input #0, mov,mp4,m4a,3gp,3g2,mj2, from 'a.mp4':\n"
        "  Duration: 00:00:12.34, start: 0.000000, bitrate: 1200 kb/s\n"
        "  Stream #0:0[0x1](und): Video: h264 (High) (avc1 / 0x31637661), "
        "yuv420p(tv, bt709, progressive), 720x1280 [SAR 1:1 DAR 9:16], 30 fps\n"
        "  Stream #0:1[0x2](und): Audio: aac (LC) (mp4a / 0x6134706D), 44100 Hz, stereo\n"
    )

    def test_plain(self) -> None:
        info = parse_probe_output(self.PLAIN)
        self.assertEqual((info.width, info.height), (720, 1280))
        self.assertAlmostEqual(info.duration, 12.34)
        self.assertTrue(info.has_audio)

    def test_rotate_tag(self) -> None:
        text = self.PLAIN.replace("720x1280", "1280x720") + "      rotate          : 90\n"
        info = parse_probe_output(text)
        self.assertEqual((info.width, info.height), (720, 1280))

    def test_displaymatrix(self) -> None:
        text = (
            self.PLAIN.replace("720x1280", "1280x720")
            + "      displaymatrix: rotation of -90.00 degrees\n"
        )
        info = parse_probe_output(text)
        self.assertEqual((info.width, info.height), (720, 1280))

    def test_missing_duration_and_audio(self) -> None:
        text = (
            "  Stream #0:0: Video: h264, yuv420p, 640x360, 25 fps\n"
        )
        info = parse_probe_output(text)
        self.assertEqual(info.duration, 0.0)
        self.assertFalse(info.has_audio)

    def test_no_video(self) -> None:
        with self.assertRaises(ValueError):
            parse_probe_output("Stream #0:0: Audio: aac, 44100 Hz\n")


@unittest.skipIf(FFMPEG is None, "FFmpeg no disponible")
class TestApplyBranding(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = self._tmp.name
        self.logo = os.path.join(self.dir, "logo.png")
        _make_logo(self.logo)
        self.opts = BrandingOptions(color="#0000FF", logo_path=self.logo, name="@MiPagina")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _leftovers(self) -> List[str]:
        return [n for n in os.listdir(self.dir) if ".branding.tmp" in n]

    def test_size_duration_audio_kept(self) -> None:
        clip = os.path.join(self.dir, "20260101_video.mp4")
        _make_clip(clip, 360, 640)
        before = probe_video(clip)
        progress: List[float] = []

        result = apply_branding(clip, self.opts, on_progress=progress.append)

        self.assertEqual(result, clip)
        after = probe_video(result)
        self.assertEqual((after.width, after.height), (before.width, before.height))
        self.assertAlmostEqual(after.duration, before.duration, delta=0.1)
        self.assertTrue(after.has_audio)
        self.assertTrue(progress)
        self.assertEqual(progress, sorted(progress))
        self.assertEqual(progress[-1], 1.0)
        self.assertEqual(self._leftovers(), [])

    def test_no_audio(self) -> None:
        clip = os.path.join(self.dir, "mute.mp4")
        _make_clip(clip, 360, 640, audio=False)
        result = apply_branding(clip, BrandingOptions(color="#00FF00"))
        info = probe_video(result)
        self.assertEqual((info.width, info.height), (360, 640))
        self.assertFalse(info.has_audio)

    def test_corrupt_video_kept(self) -> None:
        clip = os.path.join(self.dir, "broken.mp4")
        data = b"this is not a video" * 100
        Path(clip).write_bytes(data)
        with self.assertRaises(BrandingError) as ctx:
            apply_branding(clip, self.opts)
        self.assertEqual(ctx.exception.video_path, clip)
        self.assertEqual(Path(clip).read_bytes(), data)
        self.assertEqual(self._leftovers(), [])
        self.assertEqual(
            [n for n in os.listdir(tempfile.gettempdir()) if n.startswith("magoloader_overlay_")],
            [],
        )


class TestBrandingSettings(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = self._tmp.name
        self.file = os.path.join(self.dir, "branding.json")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_round_trip(self) -> None:
        logo = os.path.join(self.dir, "logo.png")
        _make_logo(logo)
        settings = BrandingSettings(enabled=True, color_text="#12ab", logo_path=logo, name="@Página")
        save_settings(settings, self.file)
        self.assertEqual(load_settings(self.file), settings)

    def test_missing_and_corrupt(self) -> None:
        self.assertEqual(load_settings(self.file), BrandingSettings())
        Path(self.file).write_text("not json", encoding="utf-8")
        self.assertEqual(load_settings(self.file), BrandingSettings())
        Path(self.file).write_text('{"enabled": "yes", "name": 3, "color_text": "#FFF"}', encoding="utf-8")
        loaded = load_settings(self.file)
        self.assertFalse(loaded.enabled)
        self.assertEqual(loaded.name, "")
        self.assertEqual(loaded.color_text, "#FFF")

    def test_missing_logo_file(self) -> None:
        save_settings(BrandingSettings(logo_path=os.path.join(self.dir, "gone.png")), self.file)
        self.assertIsNone(load_settings(self.file).logo_path)

    def test_to_options(self) -> None:
        self.assertIsNone(BrandingSettings(enabled=False, color_text="zz").to_options())
        with self.assertRaises(ValueError):
            BrandingSettings(enabled=True, color_text="zz").to_options()
        opts = BrandingSettings(enabled=True, color_text="0af", name="  @Yo ").to_options()
        self.assertEqual((opts.color, opts.logo_path, opts.name), ("#00AAFF", None, "@Yo"))

    def test_store_logo_copy(self) -> None:
        src = os.path.join(self.dir, "orig.png")
        _make_logo(src)
        dest = store_logo_copy(src, os.path.join(self.dir, "app", "branding_logo.png"))
        os.remove(src)
        self.assertEqual(load_logo(dest).mode, "RGBA")
        bad = os.path.join(self.dir, "bad.png")
        Path(bad).write_text("x", encoding="utf-8")
        with self.assertRaises(ValueError):
            store_logo_copy(bad, dest)
        self.assertEqual(load_logo(dest).size, (200, 200))


if __name__ == "__main__":
    unittest.main()
