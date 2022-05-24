# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

# PySide6 tutorial 3


import sys

from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QApplication, QPushButton, QWidget)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = QWidget()
    window.resize(200, 120)

    quit = QPushButton("Quit", window)
    quit.setFont(QFont("Times", 18, QFont.Bold))
    quit.setGeometry(10, 40, 180, 40)
    quit.clicked.connect(app.quit)

    window.show()
    sys.exit(app.exec())
