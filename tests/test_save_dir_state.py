# -*- coding: utf-8 -*-
"""Tests de SaveDirState (carpeta compartida entre pestañas)."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from magoloader.ui.state import SaveDirState  # noqa: E402


class TestSaveDirState(unittest.TestCase):
    """Todos los suscriptores reciben la nueva carpeta."""

    def test_subscribers_notified_and_folder_created(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            state = SaveDirState(tmp)
            received_a: list = []
            received_b: list = []
            state.subscribe(received_a.append)
            state.subscribe(received_b.append)

            new_dir = str(Path(tmp) / "nueva" / "carpeta")
            state.set(new_dir)

            self.assertEqual(state.get(), new_dir)
            self.assertEqual(received_a, [new_dir])
            self.assertEqual(received_b, [new_dir])
            self.assertTrue(Path(new_dir).is_dir())

    def test_empty_path_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            state = SaveDirState(tmp)
            calls: list = []
            state.subscribe(calls.append)
            state.set("")
            self.assertEqual(state.get(), tmp)
            self.assertEqual(calls, [])


if __name__ == "__main__":
    unittest.main()
