# Copyright (C) 2024 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the Qt Simple RHI Widget Example example from Qt v6.x"""

import sys

from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget

from examplewidget import ExampleRhiWidget
import rc_simplerhiwidget  # noqa F:401


class Widget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self._rhi_widget = ExampleRhiWidget(self)
        layout.addWidget(self._rhi_widget)

    def closeEvent(self, e):
        self._rhi_widget.releaseResources()
        e.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    w = Widget()
    w.resize(1280, 720)
    w.show()
    exit_code = app.exec()
    del w
    sys.exit(exit_code)
