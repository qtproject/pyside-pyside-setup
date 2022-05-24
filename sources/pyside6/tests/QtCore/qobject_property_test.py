# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for QObject property and setProperty'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject, Property, Signal


class MyObjectWithNotifyProperty(QObject):
    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self.p = 0

    def readP(self):
        return self.p

    def writeP(self, v):
        self.p = v
        self.notifyP.emit()

    notifyP = Signal()
    myProperty = Property(int, readP, fset=writeP, notify=notifyP)


class PropertyWithNotify(unittest.TestCase):
    def called(self):
        self.called_ = True

    def testNotify(self):
        self.called_ = False
        obj = MyObjectWithNotifyProperty()
        obj.notifyP.connect(self.called)
        obj.myProperty = 10
        self.assertTrue(self.called_)

    def testHasProperty(self):
        o = MyObjectWithNotifyProperty()
        o.setProperty("myProperty", 10)
        self.assertEqual(o.myProperty, 10)
        self.assertEqual(o.property("myProperty"), 10)


if __name__ == '__main__':
    unittest.main()
