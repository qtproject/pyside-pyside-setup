# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtWidgets import QDialog, QLineEdit, QVBoxLayout

# Python binding from the C++ widget
from wiggly import WigglyWidget as WigglyWidgetCPP

# Python-only widget
from wigglywidget import WigglyWidget as WigglyWidgetPY


class Dialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        wiggly_widget_py = WigglyWidgetPY(self)
        wiggly_widget_cpp = WigglyWidgetCPP(self)
        lineEdit = QLineEdit(self)

        layout = QVBoxLayout(self)
        layout.addWidget(wiggly_widget_py)
        layout.addWidget(wiggly_widget_cpp)
        layout.addWidget(lineEdit)
        lineEdit.setClearButtonEnabled(True)
        wiggly_widget_py.running = True
        wiggly_widget_cpp.setRunning(True)

        lineEdit.textChanged.connect(wiggly_widget_py.setText)
        lineEdit.textChanged.connect(wiggly_widget_cpp.setText)
        lineEdit.setText("🖖 Hello world!")

        self.setWindowTitle("Wiggly")
        self.resize(360, 145)
