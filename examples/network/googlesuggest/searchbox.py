# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtCore import Slot
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QLineEdit

from googlesuggest import GSuggestCompletion


class SearchBox(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.completer = GSuggestCompletion(self)

        self.returnPressed.connect(self.do_search)
        self.setWindowTitle("Search with Google")

        self.adjustSize()
        self.resize(400, self.height())
        self.setFocus()

    @Slot()
    def do_search(self):
        self.completer.prevent_suggest()
        url = f"https://www.google.com/search?q={self.text()}"
        QDesktopServices.openUrl(url)
