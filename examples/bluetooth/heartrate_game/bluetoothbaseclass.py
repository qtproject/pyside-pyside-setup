# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtCore import QObject, Property, Signal, Slot


class BluetoothBaseClass(QObject):

    errorChanged = Signal()
    infoChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_error = ""
        self.m_info = ""

    @Property(str, notify=errorChanged)
    def error(self):
        return self.m_error

    @error.setter
    def error(self, e):
        if self.m_error != e:
            self.m_error = e
            self.errorChanged.emit()

    @Property(str, notify=infoChanged)
    def info(self):
        return self.m_info

    @info.setter
    def info(self, i):
        if self.m_info != i:
            self.m_info = i
            self.infoChanged.emit()

    @Slot()
    def clearMessages(self):
        self.info = ""
        self.error = ""
