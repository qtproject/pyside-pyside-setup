# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations


from PySide6.QtCore import QObject, Property, Signal


class Document(QObject):

    textChanged = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._text = ''

    def text(self):
        return self._text

    def setText(self, t):
        if t != self._text:
            self._text = t
            self.textChanged.emit(t)

    text = Property(str, text, setText, notify=textChanged)
