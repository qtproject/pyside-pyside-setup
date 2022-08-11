# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import sys

from PySide6.QtBluetooth import QBluetoothLocalDevice
from PySide6.QtQml import QmlElement
from PySide6.QtCore import QObject, Property, Signal, Slot

from heartrate_global import simulator

# To be used on the @QmlElement decorator
# (QML_IMPORT_MINOR_VERSION is optional)
QML_IMPORT_NAME = "Shared"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
class ConnectionHandler(QObject):

    deviceChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_localDevice = QBluetoothLocalDevice()
        self.m_localDevice.hostModeStateChanged.connect(self.hostModeChanged)

    @Property(bool, notify=deviceChanged)
    def alive(self):
        if sys.platform == "darwin":
            return True
        if simulator:
            return True
        return (self.m_localDevice.isValid()
                and self.m_localDevice.hostMode() != QBluetoothLocalDevice.HostPoweredOff)

    @Property(bool, constant=True)
    def requiresAddressType(self):
        return sys.platform == "linux"  # QT_CONFIG(bluez)?

    @Property(str, notify=deviceChanged)
    def name(self):
        return self.m_localDevice.name()

    @Property(str, notify=deviceChanged)
    def address(self):
        return self.m_localDevice.address().toString()

    @Slot(QBluetoothLocalDevice.HostMode)
    def hostModeChanged(self, mode):
        self.deviceChanged.emit()
