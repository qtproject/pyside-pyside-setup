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

from PySide6.QtQmlFeatures import computed


class ComputedTest(unittest.TestCase):
    """Tests for the @computed method decorator."""

    def test_computed_stores_metadata(self):
        """@computed stores dep names in _pyside_computed attribute."""
        @computed("price", "quantity")
        def total(self):
            return 0

        meta = getattr(total, "_pyside_computed", None)
        self.assertIsInstance(meta, list)
        self.assertIn("price", meta)
        self.assertIn("quantity", meta)

    def test_computed_requires_at_least_one_dep(self):
        """@computed raises TypeError with no arguments."""
        with self.assertRaises(TypeError):
            @computed()
            def bad(self):
                return 0

    def test_computed_rejects_non_string_dep(self):
        """@computed raises TypeError if a dep name is not a string."""
        with self.assertRaises(TypeError):
            @computed(42)
            def bad(self):
                return 0

    def test_computed_stores_multiple_deps(self):
        """@computed with multiple dep names stores all of them."""
        @computed("a", "b", "c")
        def fn(self):
            return 0

        meta = getattr(fn, "_pyside_computed", None)
        self.assertIsInstance(meta, list)
        self.assertEqual(sorted(meta), ["a", "b", "c"])

    def test_computed_rejects_non_callable(self):
        """@computed raises TypeError if applied to a non-callable."""
        with self.assertRaises(TypeError):
            computed("price")(42)

    def test_computed_returns_original_function(self):
        """@computed returns the original function object unchanged."""
        def fn(self):
            return 0
        result = computed("price")(fn)
        self.assertIs(result, fn)


if __name__ == "__main__":
    unittest.main()
