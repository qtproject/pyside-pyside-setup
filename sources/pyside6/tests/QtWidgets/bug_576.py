# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

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
        self.assertTrue(isinstance(button, QPushButton))

    @unittest.skipUnless(hasattr(sys, "getrefcount"), f"{sys.implementation.name} has no refcount")
    def testWidgetParent(self):
        self._destroyed = False
        app = QApplication(sys.argv)
        w = QWidget()

        b = QPushButton("test")
        b.destroyed[QObject].connect(self.onButtonDestroyed)
        self.assertEqual(sys.getrefcount(b), 2)
        b.setParent(w)
        self.assertEqual(sys.getrefcount(b), 3)
        b.parent()
        self.assertEqual(sys.getrefcount(b), 3)
        b.setParent(None)
        self.assertEqual(sys.getrefcount(b), 2)
        del b
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        self.assertTrue(self._destroyed)


if __name__ == '__main__':
    unittest.main()

