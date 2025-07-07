# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
from __future__ import annotations

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QInputDialog, QDialog
from helper.usesqapplication import UsesQApplication


def is_exposed(widget):
    result = False
    if widget.isVisible():
        handle = widget.windowHandle()
        if handle:
            result = handle.isExposed()
    return result


class TestInputDialog(UsesQApplication):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._timer = None

    def setUp(self):
        super().setUp()
        if not self._timer:
            self._timer = QTimer()
            self._timer.setInterval(50)
            self._timer.timeout.connect(self._timer_handler)
            self._timer.start()

    def _timer_handler(self):
        """Periodically check for the dialog to appear and close it."""
        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, QDialog) and is_exposed(widget):
                widget.reject()

    def testGetDouble(self):
        self.assertEqual(QInputDialog.getDouble(None, "title", "label"), (0.0, False))

    def testGetInt(self):
        self.assertEqual(QInputDialog.getInt(None, "title", "label"), (0, False))

    def testGetItem(self):
        (item, bool) = QInputDialog.getItem(None, "title", "label", ["1", "2", "3"])
        self.assertEqual(str(item), "1")

    def testGetText(self):
        (text, bool) = QInputDialog.getText(None, "title", "label")
        self.assertEqual(str(text), "")


if __name__ == '__main__':
    unittest.main()
