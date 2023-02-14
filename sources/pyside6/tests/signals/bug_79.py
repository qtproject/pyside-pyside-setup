# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import gc
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtGui import QStandardItemModel
from PySide6.QtWidgets import QApplication, QTreeView


try:
    from sys import gettotalrefcount
    skiptest = False
except ImportError:
    skiptest = True


class ConnectTest(unittest.TestCase):

    def callback(self, o):
        print("callback")
        self._called = o

    def testNoLeaks_ConnectAndDisconnect(self):
        self._called = None
        app = QApplication([])
        o = QTreeView()
        o.setModel(QStandardItemModel())
        o.selectionModel().destroyed.connect(self.callback)
        o.selectionModel().destroyed.disconnect(self.callback)
        gc.collect()
        # if this is no debug build, then we check at least that
        # we do not crash any longer.
        for idx in range(200):
            # PYSIDE-2230: Warm-up is necessary before measuring, because
            # the code changes the constant parts after some time.
            o.selectionModel().destroyed.connect(self.callback)
            o.selectionModel().destroyed.disconnect(self.callback)
        if not skiptest:
            total = gettotalrefcount()
        for idx in range(1000):
            o.selectionModel().destroyed.connect(self.callback)
            o.selectionModel().destroyed.disconnect(self.callback)
        gc.collect()
        if not skiptest:
            delta = gettotalrefcount() - total
            print("delta total refcount =", delta)
            self.assertTrue(abs(delta) < 10)


if __name__ == '__main__':
    unittest.main()
