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

from PySide6.QtQmlFeatures import watch, Change


class WatchTest(unittest.TestCase):
    """Tests for the @watch method decorator."""

    def test_change_object_fields(self):
        """Change objects hold name/old/new/owner correctly."""
        c = Change("price", 10, 20, self)
        self.assertEqual(c.name, "price")
        self.assertEqual(c.old, 10)
        self.assertEqual(c.new, 20)
        self.assertEqual(c.owner, self)

    def test_change_from_qmlfeatures(self):
        """Change can be imported from PySide6.QtQmlFeatures."""
        from PySide6.QtQmlFeatures import Change as QmlChange
        c = QmlChange("x", 1, 2, None)
        self.assertIsInstance(c, Change)

    def test_watch_stores_metadata(self):
        """@watch stores property name in _pyside_watch attribute."""
        @watch("price")
        def on_price(self, change):
            pass

        self.assertEqual(getattr(on_price, "_pyside_watch", None), ["price"])

    def test_watch_multiple_stacked(self):
        """Stacking @watch accumulates property names."""
        @watch("price")
        @watch("quantity")
        def handler(self, change):
            pass

        watched = getattr(handler, "_pyside_watch", [])
        self.assertIn("price", watched)
        self.assertIn("quantity", watched)

    def test_watch_requires_change_param(self):
        """@watch raises TypeError if function doesn't accept a change param."""
        with self.assertRaises(TypeError):
            @watch("price")
            def bad(self):
                pass


if __name__ == "__main__":
    unittest.main()
