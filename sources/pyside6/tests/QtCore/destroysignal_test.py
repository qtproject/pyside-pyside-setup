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

from PySide6.QtCore import QTimer, QObject


class TestDestroySignal(unittest.TestCase):
    def onObjectDestroyed(self, timer):
        self.assertTrue(isinstance(timer, QObject))
        self._destroyed = True

    def testSignal(self):
        self._destroyed = False
        t = QTimer()
        t.destroyed[QObject].connect(self.onObjectDestroyed)
        del t
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        # PYSIDE-535: Why do I need to do it twice, here?
        gc.collect()
        self.assertTrue(self._destroyed)

    def testWithParent(self):
        self._destroyed = False
        p = QTimer()
        t = QTimer(p)
        t.destroyed[QObject].connect(self.onObjectDestroyed)
        del p
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        # PYSIDE-535: Why do I need to do it twice, here?
        gc.collect()
        self.assertTrue(self._destroyed)


if __name__ == '__main__':
    unittest.main()

