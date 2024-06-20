# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the hello_speak example from Qt v6.x"""

import sys

from PySide6.QtCore import QLoggingCategory
from PySide6.QtWidgets import QApplication

from mainwindow import MainWindow


if __name__ == "__main__":
    QLoggingCategory.setFilterRules("qt.speech.tts=true\nqt.speech.tts.*=true")

    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
