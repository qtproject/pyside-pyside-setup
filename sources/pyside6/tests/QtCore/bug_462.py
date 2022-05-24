# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject, QCoreApplication, QEvent, QThread


class MyEvent(QEvent):
    def __init__(self, i):
        print("TYPE:", type(QEvent.User))
        super().__init__(QEvent.Type(QEvent.User + (0 if sys.pyside63_option_python_enum else 100)))
        self.i = i


class MyThread (QThread):
    def __init__(self, owner):
        super().__init__()
        self.owner = owner

    def run(self):
        for i in range(3):
            e = MyEvent(i)
            QCoreApplication.postEvent(self.owner, e)


class MyBaseObject(QObject):
    def __init__(self):
        super().__init__()
        self.events = []
        self.t = MyThread(self)
        self.t.start()

    def customEvent(self, event):
        self.events.append(event)
        if len(self.events) == 3:
            self.t.wait()
            self.app.quit()


class CheckForEventsTypes(unittest.TestCase):
    def testTypes(self):
        o = MyBaseObject()
        o.app = QCoreApplication(sys.argv)
        o.app.exec()
        for e in o.events:
            self.assertTrue(isinstance(e, MyEvent))
        o.app = None


if __name__ == '__main__':
    unittest.main()
