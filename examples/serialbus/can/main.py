# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

import sys

from PySide6.QtCore import QCoreApplication, QLoggingCategory
from PySide6.QtWidgets import QApplication
from mainwindow import MainWindow

"""PySide6 port of the CAN example from Qt v6.x"""


if __name__ == "__main__":
    QLoggingCategory.setFilterRules("qt.canbus* = true")
    a = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(QCoreApplication.exec())
