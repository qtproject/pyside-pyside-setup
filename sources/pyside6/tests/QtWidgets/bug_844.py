# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import sys
import os

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths()

from PySide6.QtWidgets import QApplication, QLabel
from PySide6.QtCore import QObject, QTimer


class QtKeyPressListener(QObject):
    def __init__(self, obj):
        super().__init__()
        obj.installEventFilter(self)

    def eventFilter(self, obj, event):
        # This used to crash here due to a misbehaviour of type discovery!
        return QObject.eventFilter(self, obj, event)


app = QApplication([])
key_listener = QtKeyPressListener(app)
w = QLabel('Hello')
w.show()
QTimer.singleShot(0, w.close)
app.exec()
