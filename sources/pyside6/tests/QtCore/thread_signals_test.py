# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

''' Test case for QObject.signalsBlocked() and blockSignal()'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject, SIGNAL, QFile, QThread, QTimer, Qt
from helper.usesqapplication import UsesQApplication


class MyThread(QThread):

    def run(self):
        self.emit(SIGNAL("test(const QString&)"), "INdT - PySide")


class TestThreadSignal(UsesQApplication):

    __called__ = True

    def _callback(self, msg):
        self.assertEqual(msg, "INdT - PySide")
        self.__called__ = True
        self.app.quit()

    def testThread(self):
        t = MyThread()
        QObject.connect(t, SIGNAL("test(const QString&)"), self._callback)
        t.start()

        self.app.exec()
        t.wait()
        self.assertTrue(self.__called__)


if __name__ == '__main__':
    unittest.main()
