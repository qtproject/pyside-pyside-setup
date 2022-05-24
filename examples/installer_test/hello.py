# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

"""
hello.py
--------

This simple script shows a label with changing "Hello World" messages.
It can be used directly as a script, but we use it also to automatically
test PyInstaller or Nuitka. See testing/wheel_tester.py .

When compiled with Nuitka or used with PyInstaller, it automatically
stops its execution after 2 seconds.
"""

import sys
import random
import platform
import time

from PySide6.QtWidgets import (QApplication, QLabel, QPushButton,
                               QVBoxLayout, QWidget)
from PySide6.QtCore import Slot, Qt, QTimer

is_compiled = "__compiled__" in globals()   # Nuitka
auto_quit = "Nuitka" if is_compiled else "PyInst"


class MyWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.hello = ["Hallo Welt", "你好，世界", "Hei maailma",
            "Hola Mundo", "Привет мир"]

        self.button = QPushButton("Click me!")
        self.text = QLabel(f"Hello World auto_quit={auto_quit}")
        self.text.setAlignment(Qt.AlignCenter)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)

        # Connecting the signal
        self.button.clicked.connect(self.magic)

    @Slot()
    def magic(self):
        self.text.setText(random.choice(self.hello))


if __name__ == "__main__":
    print("Start of hello.py       ", time.ctime())
    print("  sys.version         = ", sys.version.splitlines()[0])
    print("  platform.platform() = ", platform.platform())

    app = QApplication()

    widget = MyWidget()
    widget.resize(800, 600)
    widget.show()
    if auto_quit:
        milliseconds = 2 * 1000  # run 2 second
        QTimer.singleShot(milliseconds, app.quit)
    retcode = app.exec()
    print("End of hello.py        ", time.ctime())
    sys.exit(retcode)
