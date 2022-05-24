# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

# PySide6 tutorial 4


import sys

from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QApplication, QPushButton, QWidget)


class MyWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedSize(200, 120)

        self.quit = QPushButton("Quit", self)
        self.quit.setGeometry(62, 40, 75, 30)
        self.quit.setFont(QFont("Times", 18, QFont.Bold))

        self.quit.clicked.connect(qApp.quit)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = MyWidget()
    widget.show()
    sys.exit(app.exec())
