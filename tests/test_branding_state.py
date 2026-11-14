# -*- coding: utf-8 -*-
"""Tests de BrandingState (ajustes de personalización compartidos entre pestañas)."""

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from magoloader.core.branding_settings import BrandingSettings, load_settings  # noqa: E402
from magoloader.ui.state import BrandingState  # noqa: E402


class TestBrandingState(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.file = os.path.join(self._tmp.name, "branding.json")
        self.state = BrandingState(BrandingSettings(), path=self.file)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_update_notifies_and_saves(self) -> None:
        received_a: list = []
        received_b: list = []
        self.state.subscribe(received_a.append)
        self.state.subscribe(received_b.append)

        self.state.update(enabled=True, name="@Yo")

        expected = BrandingSettings(enabled=True, name="@Yo")
        self.assertEqual(self.state.get(), expected)
        self.assertEqual(received_a, [expected])
        self.assertEqual(received_b, [expected])
        self.assertEqual(load_settings(self.file), expected)

    def test_no_change_no_notification(self) -> None:
        calls: list = []
        self.state.subscribe(calls.append)
        self.state.update(enabled=False)
        self.assertEqual(calls, [])

    def test_lock_counter(self) -> None:
        events: list = []
        self.state.subscribe_lock(events.append)
        self.state.set_locked(True)
        self.state.set_locked(True)
        self.state.set_locked(False)
        self.assertTrue(self.state.is_locked())
        self.state.set_locked(False)
        self.assertFalse(self.state.is_locked())
        self.state.set_locked(False)  # no baja de cero
        self.assertEqual(events, [True, False])


if __name__ == "__main__":
    unittest.main()
