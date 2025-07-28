# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
from __future__ import annotations

""" Unittest for bug #576 """
""" http://bugs.openbossa.org/show_bug.cgi?id=576 """

import gc
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QApplication, QPushButton, QWidget


class Bug576(unittest.TestCase):
    def onButtonDestroyed(self, button):
        self._destroyed = True

    @unittest.skipUnless(hasattr(sys, "getrefcount"), f"{sys.implementation.name} has no refcount")
    def testWidgetParent(self):
        self._destroyed = False
        app = QApplication(sys.argv)  # noqa: F841
        w = QWidget()

        b = QPushButton("test")
        b.destroyed[QObject].connect(self.onButtonDestroyed)
        base_ref_count = sys.getrefcount(b)
        b.setParent(w)
        self.assertEqual(sys.getrefcount(b), base_ref_count + 1)
        b.parent()
        self.assertEqual(sys.getrefcount(b), base_ref_count + 1)
        b.setParent(None)
        self.assertEqual(sys.getrefcount(b), base_ref_count)
        del b
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        self.assertTrue(self._destroyed)


if __name__ == '__main__':
    unittest.main()
