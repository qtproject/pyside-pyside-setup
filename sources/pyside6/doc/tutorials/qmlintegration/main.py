# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import sys
from pathlib import Path

from PySide6.QtCore import QObject, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, QmlElement
from PySide6.QtQuickControls2 import QQuickStyle

import style_rc  # noqa F401

# To be used on the @QmlElement decorator
# (QML_IMPORT_MINOR_VERSION is optional)
QML_IMPORT_NAME = "io.qt.textproperties"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
class Bridge(QObject):

    @Slot(str, result=str)
    def getColor(self, s):
        if s.lower() == "red":
            return "#ef9a9a"
        if s.lower() == "green":
            return "#a5d6a7"
        if s.lower() == "blue":
            return "#90caf9"
        return "white"

    @Slot(float, result=int)
    def getSize(self, s):
        size = int(s * 34)
        return max(1, size)

    @Slot(str, result=bool)
    def getItalic(self, s):
        return s.lower() == "italic"

    @Slot(str, result=bool)
    def getBold(self, s):
        return s.lower() == "bold"

    @Slot(str, result=bool)
    def getUnderline(self, s):
        return s.lower() == "underline"


if __name__ == '__main__':
    app = QGuiApplication(sys.argv)
    QQuickStyle.setStyle("Material")
    engine = QQmlApplicationEngine()

    # Get the path of the current directory, and then add the name
    # of the QML file, to load it.
    qml_file = Path(__file__).parent / 'view.qml'
    engine.load(qml_file)

    if not engine.rootObjects():
        sys.exit(-1)

    ex = app.exec()
    del engine
    sys.exit(ex)
