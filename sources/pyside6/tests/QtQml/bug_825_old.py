# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

"""
This is the now incorrect old version from Python 2.
It happens to work in another way and will be retained.
"""

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.helper import quickview_errorstring

from PySide6.QtCore import Qt, QUrl, QTimer
from PySide6.QtGui import QGuiApplication, QPen
from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtQml import qmlRegisterType
from PySide6.QtQuick import QQuickView, QQuickItem, QQuickPaintedItem

paintCalled = False


class MetaA(type):
    pass


class A(object):
    __metaclass__ = MetaA


MetaB = type(QQuickPaintedItem)
B = QQuickPaintedItem


class MetaC(MetaA, MetaB):
    pass


class C(A, B):
    __metaclass__ = MetaC


class Bug825 (C):
    def __init__(self, parent=None):
        QQuickPaintedItem.__init__(self, parent)

    def paint(self, painter):
        global paintCalled
        pen = QPen(Qt.black, 2)
        painter.setPen(pen)
        painter.drawPie(self.boundingRect(), 0, 128)
        paintCalled = True


class TestBug825 (unittest.TestCase):
    def testIt(self):
        global paintCalled
        app = QGuiApplication([])
        qmlRegisterType(Bug825, 'bugs', 1, 0, 'Bug825')
        self.assertRaises(TypeError, qmlRegisterType, A, 'bugs', 1, 0, 'A')

        view = QQuickView()
        file = Path(__file__).resolve().parent / 'bug_825.qml'
        self.assertTrue(file.is_file())
        view.setSource(QUrl.fromLocalFile(file))
        self.assertTrue(view.rootObject(), quickview_errorstring(view))
        view.show()
        QTimer.singleShot(250, view.close)
        app.exec()
        self.assertTrue(paintCalled)


if __name__ == '__main__':
    unittest.main()
