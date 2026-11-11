# -*- coding: utf-8 -*-
"""Tests de validación de URLs de video de TikTok."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from magoloader.utils import normalize_tiktok_video_url  # noqa: E402


class TestNormalizeTikTokVideoUrl(unittest.TestCase):
    """Formatos aceptados y rechazados por normalize_tiktok_video_url."""

    def test_accepted_formats(self) -> None:
        cases = {
            "https://www.tiktok.com/@user.name/video/7301234567890123456":
                "https://www.tiktok.com/@user.name/video/7301234567890123456",
            "https://tiktok.com/@user/video/123": "https://tiktok.com/@user/video/123",
            "https://m.tiktok.com/@user/video/123/": "https://m.tiktok.com/@user/video/123/",
            "http://www.tiktok.com/@user/video/123": "https://www.tiktok.com/@user/video/123",
            "https://m.tiktok.com/v/7301234567890123456.html":
                "https://m.tiktok.com/v/7301234567890123456.html",
            "https://www.tiktok.com/t/ZTRabc123/": "https://www.tiktok.com/t/ZTRabc123/",
            "https://vm.tiktok.com/ZMabc123/": "https://vm.tiktok.com/ZMabc123/",
            "https://vt.tiktok.com/ZSabc-12_3": "https://vt.tiktok.com/ZSabc-12_3",
            "HTTPS://WWW.TIKTOK.COM/@user/video/123": "https://www.tiktok.com/@user/video/123",
        }
        for raw, expected in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(normalize_tiktok_video_url(raw), expected)

    def test_missing_scheme_and_whitespace(self) -> None:
        self.assertEqual(
            normalize_tiktok_video_url("  www.tiktok.com/@user/video/123  "),
            "https://www.tiktok.com/@user/video/123",
        )
        self.assertEqual(
            normalize_tiktok_video_url("vm.tiktok.com/ZMabc123/"),
            "https://vm.tiktok.com/ZMabc123/",
        )

    def test_query_parameters_kept(self) -> None:
        self.assertEqual(
            normalize_tiktok_video_url("https://www.tiktok.com/@user/video/123?is_from_webapp=1&lang=es#x"),
            "https://www.tiktok.com/@user/video/123?is_from_webapp=1&lang=es",
        )

    def test_rejected_inputs(self) -> None:
        rejected = [
            "",
            "   ",
            None,
            "hola mundo",
            "https://www.tiktok.com/@user",
            "https://www.tiktok.com/@user/",
            "https://www.tiktok.com/",
            "https://www.tiktok.com/@user/video/abc",
            "https://tiktok.com.evil.net/@user/video/123",
            "https://eviltiktok.com/@user/video/123",
            "https://www.tiktok.com.evil.net/@user/video/123",
            "https://example.com/@user/video/123",
            "https://www.youtube.com/watch?v=abc",
            "ftp://www.tiktok.com/@user/video/123",
            "https://user:pass@www.tiktok.com/@user/video/123",
            "https://vm.tiktok.com/",
            "https://vm.tiktok.com/abc/def",
            "https://www.tiktok.com/@user/video/123 extra",
        ]
        for raw in rejected:
            with self.subTest(raw=raw):
                self.assertIsNone(normalize_tiktok_video_url(raw))


if __name__ == "__main__":
    unittest.main()
