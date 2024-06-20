# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

import sys
from PySide6.QtCore import QObject, QThread, Signal, Slot
from PySide6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget


# Create a basic window with a layout and a button
class MainForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My Form")
        self.layout = QVBoxLayout()
        self.button = QPushButton("Click me!")
        self.button.clicked.connect(self.start_thread)
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)

    # Instantiate and start a new thread
    def start_thread(self):
        instanced_thread = WorkerThread(self)
        instanced_thread.start()

    # Create the Slots that will receive signals
    @Slot(str)
    def update_str_field(self, message):
        print(message)

    @Slot(int)
    def update_int_field(self, value):
        print(value)


# Signals must inherit QObject
class MySignals(QObject):
    signal_str = Signal(str)
    signal_int = Signal(int)


# Create the Worker Thread
class WorkerThread(QThread):
    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        # Instantiate signals and connect signals to the slots
        self.signals = MySignals()
        self.signals.signal_str.connect(parent.update_str_field)
        self.signals.signal_int.connect(parent.update_int_field)

    def run(self):
        # Do something on the worker thread
        a = 1 + 1
        # Emit signals whenever you want
        self.signals.signal_int.emit(a)
        self.signals.signal_str.emit("This text comes to Main thread from our Worker thread.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainForm()
    window.show()
    sys.exit(app.exec())
