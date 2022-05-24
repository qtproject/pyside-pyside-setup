# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import gc
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtWidgets import QWidget, QPushButton

from helper.usesqapplication import UsesQApplication


class TestBug1002 (UsesQApplication):
    @unittest.skipUnless(hasattr(sys, "getrefcount"), f"{sys.implementation.name} has no refcount")
    def testReturnWindow(self):
        widget = QWidget()
        button = QPushButton(widget)
        self.assertEqual(sys.getrefcount(widget), 2)
        window = button.window()
        self.assertEqual(sys.getrefcount(widget), 3)
        self.assertEqual(sys.getrefcount(window), 3)

        del widget
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()


if __name__ == '__main__':
    unittest.main()
