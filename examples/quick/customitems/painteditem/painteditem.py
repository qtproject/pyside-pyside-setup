# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from argparse import ArgumentParser, RawTextHelpFormatter
from pathlib import Path
import sys

from PySide6.QtGui import QPainter, QBrush, QColor
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QmlElement, QQmlDebuggingEnabler
from PySide6.QtCore import QUrl, Property, Signal, Qt, QPointF
from PySide6.QtQuick import QQuickPaintedItem, QQuickView

QML_IMPORT_NAME = "TextBalloonPlugin"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0  # Optional


@QmlElement
class TextBalloon(QQuickPaintedItem):

    rightAlignedChanged = Signal()

    def __init__(self, parent=None):
        self._rightAligned = False
        super().__init__(parent)

    @Property(bool, notify=rightAlignedChanged)
    def rightAligned(self):
        return self._rightAligned

    @rightAligned.setter
    def rightAligned(self, value):
        self._rightAligned = value
        self.rightAlignedChanged.emit()

    def paint(self, painter: QPainter):

        brush = QBrush(QColor("#007430"))

        painter.setBrush(brush)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        itemSize = self.size()

        painter.drawRoundedRect(0, 0, itemSize.width(), itemSize.height() - 10, 10, 10)

        if self.rightAligned:
            points = [
                QPointF(itemSize.width() - 10.0, itemSize.height() - 10.0),
                QPointF(itemSize.width() - 20.0, itemSize.height()),
                QPointF(itemSize.width() - 30.0, itemSize.height() - 10.0),
            ]
        else:
            points = [
                QPointF(10.0, itemSize.height() - 10.0),
                QPointF(20.0, itemSize.height()),
                QPointF(30.0, itemSize.height() - 10.0),
            ]
        painter.drawConvexPolygon(points)


if __name__ == "__main__":

    argument_parser = ArgumentParser(description="Scene Graph Painted Item Example",
                                     formatter_class=RawTextHelpFormatter)
    argument_parser.add_argument("-qmljsdebugger", action="store",
                                 help="Enable QML debugging")
    options = argument_parser.parse_args()
    if options.qmljsdebugger:
        QQmlDebuggingEnabler.enableDebugging(True)
    app = QApplication(sys.argv)
    view = QQuickView()
    view.setResizeMode(QQuickView.ResizeMode.SizeRootObjectToView)
    qml_file = Path(__file__).parent / "main.qml"
    view.setSource(QUrl.fromLocalFile(qml_file))

    if view.status() == QQuickView.Status.Error:
        sys.exit(-1)
    view.show()

    sys.exit(app.exec())
