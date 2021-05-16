# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for QRunnable'''

import os
import sys
import unittest
from io import StringIO

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QCoreApplication, QRunnable, QThreadPool, QThread, qDebug
from helper.usesqapplication import UsesQApplication
test_result = ""


def check_test():
    global test_result
    test_result = "test works"


class QRunnableTest(UsesQApplication):
    def testCreateWithAutoDelete(self):
        global test_result
        test_result = ""  # reset
        runnable = QRunnable.create(check_test)
        runnable.run()
        self.assertEqual(test_result, "test works")

    def testwithQThreadPool(self):
        global test_result
        test_result = ""  # reset
        runnable = QRunnable.create(check_test)
        tp = QThreadPool.globalInstance()
        tp.start(runnable)
        self.assertTrue(tp.waitForDone())
        self.assertEqual(test_result, "test works")


if __name__ == '__main__':
    unittest.main()
