#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QCoreApplication, QObject, QTimer, SIGNAL, SLOT

"""
This is a simple slot test that was updated to use the qApp "macro".
It is implicitly in builtins and does not need an import.
"""


class objTest(QObject):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ok = False

    def slot(self):
        self.ok = True
        qApp.quit()


class slotTest(unittest.TestCase):
    def quit_app(self):
        qApp.quit()

    def testBasic(self):
        timer = QTimer()
        timer.setInterval(100)

        my_obj = objTest()
        my_slot = SLOT("slot()")
        QObject.connect(timer, SIGNAL("timeout()"), my_obj, my_slot)
        timer.start(100)

        QTimer.singleShot(1000, self.quit_app)
        qApp.exec()

        self.assertTrue(my_obj.ok)


if __name__ == '__main__':
    QCoreApplication()
    unittest.main()
