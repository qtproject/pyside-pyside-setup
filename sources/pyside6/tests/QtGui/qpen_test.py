# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.usesqapplication import UsesQApplication

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPen, QPainter, QRasterWindow


class Painting(QRasterWindow):
    def __init__(self):
        super().__init__()
        self.penFromEnum = None
        self.penFromInteger = None

    def paintEvent(self, event):
        with QPainter(self) as painter:
            painter.setPen(Qt.NoPen)
            self.penFromEnum = painter.pen()
            intVal = Qt.NoPen.value if sys.pyside63_option_python_enum else int(Qt.NoPen)
            painter.setPen(intVal)
            self.penFromInteger = painter.pen()
        QTimer.singleShot(20, self.close)


class QPenTest(UsesQApplication):

    def testCtorWithCreatedEnums(self):
        '''A simple case of QPen creation using created enums.'''
        width = 0
        style = Qt.PenStyle(0)
        cap = Qt.PenCapStyle(0)
        join = Qt.PenJoinStyle(0)
        pen = QPen(Qt.blue, width, style, cap, join)

    def testSetPenWithPenStyleEnum(self):
        '''Calls QPainter.setPen with both enum and integer. Bug #511.'''
        w = Painting()
        w.show()
        w.setTitle("qpen_test")
        self.app.exec()
        self.assertEqual(w.penFromEnum.style(), Qt.NoPen)
        self.assertEqual(w.penFromInteger.style(), Qt.SolidLine)


if __name__ == '__main__':
    unittest.main()

