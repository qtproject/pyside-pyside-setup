# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

# PySide6 tutorial 1


import sys

from PySide6.QtWidgets import QApplication, QPushButton


if __name__ == '__main__':
    app = QApplication(sys.argv)

    hello = QPushButton("Hello world!")
    hello.resize(100, 30)

    hello.show()

    sys.exit(app.exec())
