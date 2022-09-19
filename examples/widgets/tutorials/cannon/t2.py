# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

# PySide6 tutorial 2


import sys

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QPushButton


if __name__ == '__main__':
    app = QApplication(sys.argv)

    quit = QPushButton("Quit")
    quit.resize(75, 30)
    quit.setFont(QFont("Times", 18, QFont.Bold))

    quit.clicked.connect(app.quit)

    quit.show()
    sys.exit(app.exec())
