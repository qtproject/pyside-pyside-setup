# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from enum import IntEnum

from PySide6.QtQml import QmlElement, QmlUncreatable
from PySide6.QtCore import QObject, Property, Signal, Slot, QEnum

QML_IMPORT_NAME = "HeartRateGame"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
@QmlUncreatable("BluetoothBaseClass is not intended to be created directly")
class BluetoothBaseClass(QObject):

    @QEnum
    class IconType(IntEnum):
        IconNone = 0
        IconBluetooth = 1
        IconError = 2
        IconProgress = 3
        IconSearch = 4

    errorChanged = Signal()
    infoChanged = Signal()
    iconChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_error = ""
        self.m_info = ""
        self.m_icon = BluetoothBaseClass.IconType.IconNone

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

    @Property(int, notify=iconChanged)
    def icon(self):
        return self.m_icon

    @icon.setter
    def icon(self, i):
        if self.m_icon != i:
            self.m_icon = i
            self.iconChanged.emit()

    @Slot()
    def clearMessages(self):
        self.info = ""
        self.error = ""
        self.icon = BluetoothBaseClass.IconType.IconNone
