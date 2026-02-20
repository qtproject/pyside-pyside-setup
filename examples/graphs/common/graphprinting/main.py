# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import sys
from pathlib import Path

from PySide6.QtCore import QCoreApplication, QSize, Qt
from PySide6.QtGui import QGuiApplication, QShortcut, QKeySequence
from PySide6.QtQuick import QQuickView

from graphprinter import GraphPrinter


if __name__ == "__main__":
    app = QGuiApplication(sys.argv)

    viewer = QQuickView()
    viewer.setTitle("Graph Printing")
    graphPrinter = GraphPrinter()
    viewer.rootContext().setContextProperty("graphPrinter", graphPrinter)
    viewer.setMinimumSize(QSize(1280, 720))
    viewer.engine().addImportPath(Path(__file__).parent)
    viewer.loadFromModule("GraphPrintingExample", "Main")
    window = viewer.rootObject()
    if not window:
        sys.exit(-1)
    quitKey = QKeySequence(QKeySequence.StandardKey.Quit)
    if not quitKey.isEmpty():
        quitShortcut = QShortcut(quitKey, window)
        quitShortcut.activated.connect(app.quit)
        quitShortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)
    viewer.setResizeMode(QQuickView.ResizeMode.SizeRootObjectToView)
    viewer.setColor(Qt.GlobalColor.white)
    viewer.show()

    ex = QCoreApplication.exec()
    del viewer
    sys.exit(ex)
