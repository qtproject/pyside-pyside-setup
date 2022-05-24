# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

"""PySide6 port of the qml/tutorials/extending-qml/chapter5-listproperties example from Qt v5.x"""

import os
from pathlib import Path
import sys

from PySide6.QtCore import Property, QUrl
from PySide6.QtGui import QGuiApplication, QPen, QPainter, QColor
from PySide6.QtQml import QmlElement, ListProperty
from PySide6.QtQuick import QQuickPaintedItem, QQuickView, QQuickItem

# To be used on the @QmlElement decorator
# (QML_IMPORT_MINOR_VERSION is optional)
QML_IMPORT_NAME = "Charts"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
class PieSlice (QQuickPaintedItem):
    def __init__(self, parent=None):
        QQuickPaintedItem.__init__(self, parent)
        self._color = QColor()
        self._fromAngle = 0
        self._angleSpan = 0

    @Property(QColor)
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = value

    @Property(int)
    def fromAngle(self):
        return self._angle

    @fromAngle.setter
    def fromAngle(self, value):
        self._fromAngle = value

    @Property(int)
    def angleSpan(self):
        return self._angleSpan

    @angleSpan.setter
    def angleSpan(self, value):
        self._angleSpan = value

    def paint(self, painter):
        pen = QPen(self._color, 2)
        painter.setPen(pen)
        painter.setRenderHints(QPainter.Antialiasing, True)
        painter.drawPie(self.boundingRect().adjusted(1, 1, -1, -1), self._fromAngle * 16, self._angleSpan * 16)


@QmlElement
class PieChart (QQuickItem):
    def __init__(self, parent=None):
        QQuickItem.__init__(self, parent)
        self._name = u''
        self._slices = []

    @Property(str)
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    def appendSlice(self, _slice):
        _slice.setParentItem(self)
        self._slices.append(_slice)

    slices = ListProperty(PieSlice, appendSlice)


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
