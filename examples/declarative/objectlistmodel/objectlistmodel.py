# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from pathlib import Path
import sys
from PySide6.QtCore import QObject, QUrl, Property, Signal
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuick import QQuickView

# This example illustrates exposing a list of QObjects as a model in QML

class DataObject(QObject):

    nameChanged = Signal()
    colorChanged = Signal()

    def __init__(self, name, color, parent=None):
        super().__init__(parent)
        self._name = name
        self._color = color

    def name(self):
        return self._name

    def setName(self, name):
        if name != self._name:
            self._name = name
            nameChanged.emit()

    def color(self):
        return self._color

    def setColor(self, color):
        if color != self._color:
            self._color = color
            colorChanged.emit()


    name = Property(str, name, setName, notify=nameChanged)
    color = Property(str, color, setColor, notify=colorChanged)


if __name__ == '__main__':
    app = QGuiApplication(sys.argv)

    dataList = [DataObject("Item 1", "red"),
                DataObject("Item 2", "green"),
                DataObject("Item 3", "blue"),
                DataObject("Item 4", "yellow")]

    view = QQuickView()
    view.setResizeMode(QQuickView.SizeRootObjectToView)
    view.setInitialProperties({"model": dataList})

    qml_file = Path(__file__).parent / "view.qml"
    view.setSource(QUrl.fromLocalFile(qml_file))
    view.show()

    r = app.exec()
    del view
    sys.exit(r)
