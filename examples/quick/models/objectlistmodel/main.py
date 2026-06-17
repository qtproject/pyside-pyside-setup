# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from pathlib import Path
import sys
from PySide6.QtCore import QObject
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuick import QQuickView
from PySide6.QtQmlFeatures import auto_properties, watch, Change

# This example illustrates exposing a list of QObjects as a model in QML


# @auto_properties turns the plain "self.name = ..." / "self.color = ..."
# assignments into real Q_PROPERTYs with nameChanged/colorChanged notify
# signals, so QML can read them as model roles and write them back. The
# @watch method then runs whenever the color is changed from QML.
@auto_properties
class DataObject(QObject):

    def __init__(self, name, color, parent=None):
        super().__init__(parent)
        self.name = name
        self.color = color

    @watch("color")
    def on_color_changed(self, change: Change):
        print(f"{self.name}: color {change.old} -> {change.new}")


if __name__ == '__main__':
    app = QGuiApplication(sys.argv)

    dataList = [DataObject("Item 1", "red"),
                DataObject("Item 2", "green"),
                DataObject("Item 3", "blue"),
                DataObject("Item 4", "yellow")]

    view = QQuickView()
    view.setResizeMode(QQuickView.ResizeMode.SizeRootObjectToView)
    view.setInitialProperties({"model": dataList})

    qml_file = Path(__file__).parent / "view.qml"
    view.engine().addImportPath(Path(__file__).parent)
    view.loadFromModule("ObjectListModel", "Main")
    view.show()

    r = app.exec()
    del view
    sys.exit(r)
