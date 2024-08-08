# Copyright (C) 2024 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import sys
from pathlib import Path

from PySide6.QtCore import QCoreApplication, QUrl, QRect, QPoint
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWebView import QtWebView
import argparse

import rc_qml  # noqa: F401


class Utils:
    @staticmethod
    def fromUserInput(userInput):
        if not userInput:
            return QUrl.fromUserInput("about:blank")
        result = QUrl.fromUserInput(userInput)
        return result if result.isValid() else QUrl.fromUserInput("about:blank")


if __name__ == "__main__":
    QtWebView.initialize()
    app = QGuiApplication(sys.argv)
    QGuiApplication.setApplicationDisplayName(QCoreApplication
                                              .translate("main", "QtWebView Example"))

    parser = argparse.ArgumentParser(description=QGuiApplication.applicationDisplayName())
    parser.add_argument("--url", nargs="?",
                        default="https://www.qt.io",
                        help="The initial URL to open.")
    args = parser.parse_args()
    initialUrl = args.url

    engine = QQmlApplicationEngine()
    context = engine.rootContext()
    context.setContextProperty("utils", Utils())
    context.setContextProperty("initialUrl", Utils.fromUserInput(initialUrl))

    geometry = QGuiApplication.primaryScreen().availableGeometry()
    if not QGuiApplication.styleHints().showIsFullScreen():
        size = geometry.size() * 4 / 5
        offset = (geometry.size() - size) / 2
        pos = geometry.topLeft() + QPoint(offset.width(), offset.height())
        geometry = QRect(pos, size)

    engine.setInitialProperties({"x": geometry.x(), "y": geometry.y(),
                                 "width": geometry.width(), "height": geometry.height()})
    qml_file = Path(__file__).parent / "main.qml"
    engine.load(QUrl.fromLocalFile(qml_file))

    if not engine.rootObjects():
        sys.exit(-1)

    ex = app.exec()
    del engine
    sys.exit(ex)
