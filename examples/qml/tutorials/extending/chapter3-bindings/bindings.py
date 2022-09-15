# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

"""PySide6 port of the qml/tutorials/extending-qml/chapter3-bindings example from Qt v5.x"""

import os
from pathlib import Path
import sys

from PySide6.QtCore import Property, Signal, Slot, QUrl, Qt
from PySide6.QtGui import QGuiApplication, QPen, QPainter, QColor
from PySide6.QtQml import QmlElement
from PySide6.QtQuick import QQuickPaintedItem, QQuickView

# To be used on the @QmlElement decorator
# (QML_IMPORT_MINOR_VERSION is optional)
QML_IMPORT_NAME = "Charts"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
class PieChart (QQuickPaintedItem):

    chartCleared = Signal()
    nameChanged = Signal()
    colorChanged = Signal()

    def __init__(self, parent=None):
        QQuickPaintedItem.__init__(self, parent)
        self._name = u''
        self._color = QColor()

    def paint(self, painter):
        pen = QPen(self._color, 2)
        painter.setPen(pen)
        painter.setRenderHints(QPainter.Antialiasing, True)
        painter.drawPie(self.boundingRect().adjusted(1, 1, -1, -1), 90 * 16, 290 * 16)

    @Property(QColor, notify=colorChanged)
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        if value != self._color:
            self._color = value
            self.update()
            self.colorChanged.emit()

    @Property(str, notify=nameChanged)
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @Slot()  # This should be something like @Invokable
    def clearChart(self):
        self.color = Qt.transparent
        self.update()
        self.chartCleared.emit()


if __name__ == '__main__':
    app = QGuiApplication(sys.argv)

    view = QQuickView()
    view.setResizeMode(QQuickView.SizeRootObjectToView)
    qml_file = os.fspath(Path(__file__).resolve().parent / 'app.qml')
    view.setSource(QUrl.fromLocalFile(qml_file))
    if view.status() == QQuickView.Error:
        sys.exit(-1)
    view.show()
    res = app.exec()
    # Deleting the view before it goes out of scope is required to make sure all child QML instances
    # are destroyed in the correct order.
    del view
    sys.exit(res)
