# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from PySide6 import QtCore
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QKeySequence
from PySide6.QtWidgets import QCheckBox, QLineEdit, QToolBar, QToolButton
from PySide6.QtWebEngineCore import QWebEnginePage


# A Find tool bar (bottom area)
class FindToolBar(QToolBar):

    find = QtCore.Signal(str, QWebEnginePage.FindFlag)

    def __init__(self):
        super().__init__()
        self._line_edit = QLineEdit()
        self._line_edit.setClearButtonEnabled(True)
        self._line_edit.setPlaceholderText("Find...")
        self._line_edit.setMaximumWidth(300)
        self._line_edit.returnPressed.connect(self._find_next)
        self.addWidget(self._line_edit)

        self._previous_button = QToolButton()
        style_icons = ':/qt-project.org/styles/commonstyle/images/'
        self._previous_button.setIcon(QIcon(style_icons + 'up-32.png'))
        self._previous_button.clicked.connect(self._find_previous)
        self.addWidget(self._previous_button)

        self._next_button = QToolButton()
        self._next_button.setIcon(QIcon(style_icons + 'down-32.png'))
        self._next_button.clicked.connect(self._find_next)
        self.addWidget(self._next_button)

        self._case_sensitive_checkbox = QCheckBox('Case Sensitive')
        self.addWidget(self._case_sensitive_checkbox)

        self._hideButton = QToolButton()
        self._hideButton.setShortcut(QKeySequence(Qt.Key_Escape))
        self._hideButton.setIcon(QIcon(style_icons + 'closedock-16.png'))
        self._hideButton.clicked.connect(self.hide)
        self.addWidget(self._hideButton)

    def focus_find(self):
        self._line_edit.setFocus()

    def _emit_find(self, backward):
        needle = self._line_edit.text().strip()
        if needle:
            flags = QWebEnginePage.FindFlag(0)
            if self._case_sensitive_checkbox.isChecked():
                flags |= QWebEnginePage.FindCaseSensitively
            if backward:
                flags |= QWebEnginePage.FindBackward
            self.find.emit(needle, flags)

    def _find_next(self):
        self._emit_find(False)

    def _find_previous(self):
        self._emit_find(True)
