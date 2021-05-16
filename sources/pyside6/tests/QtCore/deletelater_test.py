#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for QTimer.singleShot'''

import gc
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject, QTimer, QCoreApplication, SIGNAL
from helper.usesqapplication import UsesQApplication


class TestDeleteLater(UsesQApplication):
    '''Test case for function DeleteLater'''

    def testCase(self):
        o = QObject()
        o.deleteLater()
        del o
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        QTimer.singleShot(100, self.app.quit)
        self.app.exec()


if __name__ == '__main__':
    unittest.main()

