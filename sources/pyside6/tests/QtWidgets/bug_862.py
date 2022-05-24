# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0


#
# Test for bug 862, original description was:
#
# print seems to be broken at least for QGraphicsItems-derived objects. The
# attached code shows:
#
# <__main__.MyQObject object at 0xf99f38>
# <__main__.MyQWidget object at 0xf99f38>
# <PySide.QtGui.MyQGraphicsObject (this = 0x11c0d60 , parent = 0x0 , pos =
# QPointF(0, 0) , z = 0 , flags =  ( ) )  at 0xf99f38>
# <PySide.QtGui.QGraphicsItem (this = 0x11c2e60 , parent = 0x0 , pos = QPointF(0,
# 0) , z = 0 , flags =  ( ) )  at 0xf99f38>
#
# Where it should be showing something like:
#
# <__main__.MyQObject object at 0x7f55cf226c20>
# <__main__.MyQWidget object at 0x7f55cf226c20>
# <__main__.MyQGraphicsObject object at 0x7f55cf226c20>
# <__main__.MyQGraphicsItem object at 0x7f55cf226c20>
#

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QApplication, QGraphicsItem, QGraphicsWidget, QGraphicsObject, QWidget
import PySide6.QtCore


class MyQObject(QObject):
    def __init__(self):
        super().__init__()


class MyQWidget(QWidget):
    def __init__(self):
        super().__init__()


class MyQGraphicsObject(QGraphicsObject):
    def __init__(self):
        super().__init__()


class MyQGraphicsItem(QGraphicsItem):
    def __init__(self):
        super().__init__()


class TestRepr (unittest.TestCase):

    def testIt(self):

        app = QApplication([])

        self.assertEqual("<__main__.MyQObject(0x", repr(MyQObject())[:22])
        self.assertEqual("<__main__.MyQWidget(0x", repr(MyQWidget())[:22])
        self.assertEqual("<__main__.MyQGraphicsObject(0x", repr(MyQGraphicsObject())[:30])
        self.assertEqual("<__main__.MyQGraphicsItem(0x", repr(MyQGraphicsItem())[:28])

        self.assertEqual("<PySide6.QtCore.QObject(0x", repr(QObject())[:26])
        self.assertEqual("<PySide6.QtCore.QObject(0x", repr(PySide6.QtCore.QObject())[:26])
        self.assertEqual("<PySide6.QtWidgets.QWidget(0x", repr(QWidget())[:29])
        self.assertEqual("<PySide6.QtWidgets.QGraphicsWidget(0x", repr(QGraphicsWidget())[:37])


if __name__ == "__main__":
    unittest.main()
