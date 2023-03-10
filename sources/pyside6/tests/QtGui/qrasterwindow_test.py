# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Unit test for QBackingStore, QRasterWindow and QStaticText'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.usesqapplication import UsesQApplication
from PySide6.QtCore import QPoint, QRect, QSize, QTimer, Qt
from PySide6.QtGui import (QColor, QPainter, QRasterWindow, QStaticText,
                           QTextCursor, QTextDocument, QAbstractTextDocumentLayout)


# Window using convenience class QRasterWindow
class StaticTextRasterWindow(QRasterWindow):
    def __init__(self):
        super().__init__()
        self.text = QStaticText("QRasterWindow")

    def paintEvent(self, event):
        clientRect = QRect(QPoint(0, 0), self.size())
        with QPainter(self) as painter:
            painter.fillRect(clientRect, QColor(Qt.red))
            painter.drawStaticText(QPoint(10, 10), self.text)


class TextDocumentWindow(QRasterWindow):
    """PYSIDE-2252, drawing with QAbstractTextDocumentLayout.PaintContext"""

    def __init__(self):
        super().__init__()
        self.m_document = QTextDocument()
        self.m_document.setPlainText("bla bla")

    def paintEvent(self, event):
        with QPainter(self) as painter:
            clientRect = QRect(QPoint(0, 0), self.size())
            painter.fillRect(clientRect, QColor(Qt.white))
            ctx = QAbstractTextDocumentLayout.PaintContext()
            ctx.clip = clientRect

            sel = QAbstractTextDocumentLayout.Selection()
            cursor = QTextCursor(self.m_document)
            cursor.movePosition(QTextCursor.Start)
            cursor.movePosition(QTextCursor.NextWord, QTextCursor.KeepAnchor)
            sel.cursor = cursor
            sel.format.setForeground(Qt.red)
            ctx.selections = [sel]

            self.m_document.documentLayout().draw(painter, ctx)


class QRasterWindowTest(UsesQApplication):
    def test(self):
        rasterWindow = StaticTextRasterWindow()
        rasterWindow.setFramePosition(QPoint(100, 100))
        rasterWindow.resize(QSize(400, 400))
        rasterWindow.show()

        rasterWindow2 = TextDocumentWindow()
        rasterWindow2.setFramePosition(rasterWindow.frameGeometry().topRight() + QPoint(20, 0))
        rasterWindow2.resize(QSize(400, 400))
        rasterWindow2.show()

        QTimer.singleShot(100, self.app.quit)
        self.app.exec()


if __name__ == '__main__':
    unittest.main()
