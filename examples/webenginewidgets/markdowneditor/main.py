# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 Markdown Editor Example"""

import sys

from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication

from mainwindow import MainWindow
import rc_markdowneditor  # noqa: F401


if __name__ == '__main__':
    app = QApplication(sys.argv)
    QCoreApplication.setOrganizationName("QtExamples")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
