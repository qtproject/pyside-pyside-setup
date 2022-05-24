# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import gc
import os
import sys
import unittest
import weakref

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtWidgets import QMenu, QWidget, QMenuBar, QToolBar
from helper.usesqapplication import UsesQApplication


class TestQActionLifeCycle(UsesQApplication):
    def actionDestroyed(self, act):
        self._actionDestroyed = True

    def testMenu(self):
        self._actionDestroyed = False
        w = QWidget()
        menu = QMenu(w)
        act = menu.addAction("MENU")
        _ref = weakref.ref(act, self.actionDestroyed)
        act = None
        self.assertFalse(self._actionDestroyed)
        menu.clear()
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        self.assertTrue(self._actionDestroyed)

    def testMenuBar(self):
        self._actionDestroyed = False
        w = QWidget()
        menuBar = QMenuBar(w)
        act = menuBar.addAction("MENU")
        _ref = weakref.ref(act, self.actionDestroyed)
        act = None
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        self.assertFalse(self._actionDestroyed)
        menuBar.clear()
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        self.assertTrue(self._actionDestroyed)

    def testToolBar(self):
        self._actionDestroyed = False
        w = QWidget()
        toolBar = QToolBar(w)
        act = toolBar.addAction("MENU")
        _ref = weakref.ref(act, self.actionDestroyed)
        act = None
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        self.assertFalse(self._actionDestroyed)
        toolBar.clear()
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        self.assertTrue(self._actionDestroyed)


if __name__ == "__main__":
    unittest.main()
