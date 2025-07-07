# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
from __future__ import annotations

import os
import sys
import unittest
import weakref

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import Slot, QTimer
from PySide6.QtWidgets import QApplication, QDialog, QMainWindow
from helper.timedqapplication import TimedQApplication


def is_exposed(widget):
    result = False
    if widget.isVisible():
        handle = widget.windowHandle()
        if handle:
            result = handle.isExposed()
    return result


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main")
        self.dialog = None
        self._timer = QTimer()
        self._timer.setInterval(50)
        self._timer.timeout.connect(self._timer_handler)
        self._timer.start()

    @Slot()
    def execDialog(self):
        dialog = QDialog(self)
        self.dialog = weakref.ref(dialog)
        dialog.setWindowTitle("Dialog")
        dialog.setMinimumWidth(200)
        QTimer.singleShot(500, dialog.reject)
        dialog.exec()
        self.close()

    @Slot()
    def _timer_handler(self):
        """Periodically check for the dialog to appear and close it."""
        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, QDialog) and is_exposed(widget):
                widget.reject()


class DialogExecTest(TimedQApplication):
    """Test whether the parent-child relationship (dialog/main window) is removed when
       using QDialog.exec() (instead show()), preventing the dialog from leaking."""

    def setUp(self):
        super().setUp(10000)
        self._window = Window()

    def testExec(self):
        self._window.show()
        while not is_exposed(self._window):
            QApplication.processEvents()
        QTimer.singleShot(0, self._window.execDialog)
        self.app.exec()
        self.assertTrue(self._window.dialog() is None)


if __name__ == '__main__':
    unittest.main()
