# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
from __future__ import annotations

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtQmlFeatures import effect


class EffectTest(unittest.TestCase):
    """Tests for the @effect method decorator."""

    def test_effect_stores_metadata(self):
        """@effect stores property names in _pyside_effect."""
        @effect("price", "quantity")
        def refresh(self):
            pass

        props = getattr(refresh, "_pyside_effect", [])
        self.assertIn("price", props)
        self.assertIn("quantity", props)

    def test_effect_requires_at_least_one_name(self):
        """@effect raises TypeError with no arguments."""
        with self.assertRaises(TypeError):
            @effect()
            def bad(self):
                pass

    def test_effect_rejects_non_string_name(self):
        """@effect raises TypeError if an argument is not a string."""
        with self.assertRaises(TypeError):
            @effect(42)
            def bad(self):
                pass

    def test_effect_rejects_non_callable(self):
        """@effect raises TypeError if applied to a non-callable."""
        with self.assertRaises(TypeError):
            effect("price")(42)

    def test_effect_returns_original_function(self):
        """@effect returns the original function object unchanged."""
        def fn(self):
            pass
        result = effect("price")(fn)
        self.assertIs(result, fn)

    def test_effect_stacking_merges_names(self):
        """Stacking @effect decorators accumulates all property names."""
        @effect("quantity")
        @effect("price")
        def refresh(self):
            pass

        props = getattr(refresh, "_pyside_effect", [])
        self.assertIn("price", props)
        self.assertIn("quantity", props)
        self.assertEqual(len(props), 2)


if __name__ == "__main__":
    unittest.main()
