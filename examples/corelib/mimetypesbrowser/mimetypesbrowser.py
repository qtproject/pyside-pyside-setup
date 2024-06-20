# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the corelib/mimetypes/mimetypebrowser example from from Qt"""

import argparse
import sys

from mainwindow import MainWindow
from PySide6.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)

    parser = argparse.ArgumentParser(description="MimeTypesBrowser Example")
    parser.add_argument("-v", "--version", action="version", version="%(prog)s 1.0")
    args = parser.parse_args()

    mainWindow = MainWindow()
    availableGeometry = mainWindow.screen().availableGeometry()
    mainWindow.resize(availableGeometry.width() / 3, availableGeometry.height() / 2)
    mainWindow.show()

    sys.exit(app.exec())
