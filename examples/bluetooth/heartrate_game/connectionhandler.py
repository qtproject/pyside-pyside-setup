# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import sys

from PySide6.QtBluetooth import QBluetoothLocalDevice
from PySide6.QtQml import QmlElement
from PySide6.QtCore import QObject, Property, Signal, Slot, Qt, QCoreApplication

from heartrate_global import simulator, is_android

if is_android:
    from PySide6.QtCore import QBluetoothPermission

# To be used on the @QmlElement decorator
# (QML_IMPORT_MINOR_VERSION is optional)
QML_IMPORT_NAME = "HeartRateGame"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
class ConnectionHandler(QObject):

    deviceChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_hasPermission = False
        self.initLocalDevice()

    @Property(bool, notify=deviceChanged)
    def alive(self):
        if sys.platform == "darwin":
            return True
        if simulator():
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

    @Property(bool, notify=deviceChanged)
    def hasPermission(self):
        return self.m_hasPermission

    @Slot(QBluetoothLocalDevice.HostMode)
    def hostModeChanged(self, mode):
        self.deviceChanged.emit()

    def initLocalDevice(self):
        if is_android:
            permission = QBluetoothPermission()
            permission.setCommunicationModes(QBluetoothPermission.Access)
            permission_status = qApp.checkPermission(permission)
            if permission_status == Qt.PermissionStatus.Undetermined:
                qApp.requestPermission(permission, self, self.initLocalDevice)
                return
            if permission_status == Qt.PermissionStatus.Denied:
                return
            elif permission_status == Qt.PermissionStatus.Granted:
                print("[HeartRateGame] Bluetooth Permission Granted")

        self.m_localDevice = QBluetoothLocalDevice()
        self.m_localDevice.hostModeStateChanged.connect(self.hostModeChanged)
        self.m_hasPermission = True
        self.deviceChanged.emit()
