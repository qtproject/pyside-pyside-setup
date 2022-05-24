# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QCoreApplication, QObject, QTimeLine, SIGNAL


class SignalPrimitiveTypeTest(unittest.TestCase):

    def signalValueChanged(self, v):
        self.called = True
        self._app.quit()

    def createTimeLine(self):
        self.called = False
        tl = QTimeLine(10000)
        tl.valueChanged.connect(self.signalValueChanged)
        return tl

    def testTimeLine(self):
        self._valueChangedCount = 0
        self._app = QCoreApplication([])
        tl = self.createTimeLine()
        tl.start()
        self._app.exec()
        self.assertTrue(self.called)


if __name__ == '__main__':
    unittest.main()


