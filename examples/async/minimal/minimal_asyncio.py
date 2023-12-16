# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from PySide6.QtCore import (Qt, QObject, Signal, Slot)
from PySide6.QtWidgets import (QApplication, QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget)

import PySide6.QtAsyncio as QtAsyncio

import asyncio
import sys


class MainWindow(QMainWindow):

    start_signal = Signal()

    def __init__(self):
        super().__init__()

        widget = QWidget()
        self.setCentralWidget(widget)

        layout = QVBoxLayout(widget)

        self.text = QLabel("The answer is 42.")
        layout.addWidget(self.text, alignment=Qt.AlignmentFlag.AlignCenter)

        async_trigger = QPushButton(text="What is the question?")
        async_trigger.clicked.connect(self.async_start)
        layout.addWidget(async_trigger, alignment=Qt.AlignmentFlag.AlignCenter)

    @Slot()
    def async_start(self):
        self.start_signal.emit()

    async def set_text(self):
        await asyncio.sleep(1)
        self.text.setText("What do you get if you multiply six by nine?")


class AsyncHelper(QObject):

    def __init__(self, worker, entry):
        super().__init__()
        self.entry = entry
        self.worker = worker
        if hasattr(self.worker, "start_signal") and isinstance(self.worker.start_signal, Signal):
            self.worker.start_signal.connect(self.on_worker_started)

    @Slot()
    def on_worker_started(self):
        asyncio.ensure_future(self.entry())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    async_helper = AsyncHelper(main_window, main_window.set_text)

    main_window.show()

    QtAsyncio.run()
