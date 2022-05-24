# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
sys.path.append(os.fspath(Path(__file__).resolve().parents[1] / "util"))
from init_paths import init_test_paths
init_test_paths()

from PySide6.QtWidgets import QApplication, QDialog, QFileDialog
from PySide6.QtCore import QDir, QTimer


# Periodically check for the file dialog to appear and close it
dialog = None


def timerHandler():
    global dialog
    if dialog is not None:
        dialog.reject()
    else:
        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, QDialog) and widget.isVisible():
                dialog = widget


app = QApplication([])
QTimer.singleShot(30000, app.quit)  # emergency
timer = QTimer()
timer.setInterval(50)
timer.timeout.connect(timerHandler)
timer.start()

# This test for a dead lock in QFileDialog.getOpenFileNames, the test fail with a timeout if the dead lock exists.
QFileDialog.getOpenFileNames(None, "caption", QDir.homePath(), None, "", QFileDialog.DontUseNativeDialog)
