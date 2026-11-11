# -*- coding: utf-8 -*-
"""Tests de completitud de traducciones (es, en, pt).

Ejecutar con:  python -m unittest discover -s tests
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from check_i18n import find_problems  # noqa: E402


class TestTranslationsComplete(unittest.TestCase):
    """Cada clave debe existir, no estar vacía y tener los mismos placeholders en todos los idiomas."""

    def test_all_languages_have_all_keys(self) -> None:
        problems = find_problems()
        self.assertEqual(problems, [], "\n" + "\n".join(problems))


if __name__ == "__main__":
    unittest.main()
