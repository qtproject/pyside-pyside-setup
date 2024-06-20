# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtWidgets import QWidget, QHBoxLayout

from glwidget import GLWidget


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self._glwidget1 = GLWidget(self)
        layout.addWidget(self._glwidget1)
        self._glwidget2 = GLWidget(self)
        layout.addWidget(self._glwidget2)

    def closeEvent(self, event):
        self._glwidget1.stop_rendering()
        self._glwidget2.stop_rendering()
        event.accept()
