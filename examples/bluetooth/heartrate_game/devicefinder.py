# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations
import sys

from PySide6.QtBluetooth import (QBluetoothDeviceDiscoveryAgent,
                                 QBluetoothDeviceInfo)
from PySide6.QtQml import QmlElement
from PySide6.QtCore import QTimer, Property, Signal, Slot, Qt

from bluetoothbaseclass import BluetoothBaseClass
from deviceinfo import DeviceInfo
from heartrate_global import simulator, is_android, error_not_nuitka

if is_android or sys.platform == "darwin":
    from PySide6.QtCore import QBluetoothPermission

# To be used on the @QmlElement decorator
# (QML_IMPORT_MINOR_VERSION is optional)
QML_IMPORT_NAME = "HeartRateGame"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
class DeviceFinder(BluetoothBaseClass):

    scanningChanged = Signal()
    devicesChanged = Signal()

    def __init__(self, handler, parent=None):
        super().__init__(parent)
        self.m_deviceHandler = handler
        self.m_devices = []
        self.m_demoTimer = QTimer()
#! [devicediscovery-1]
        self.m_deviceDiscoveryAgent = QBluetoothDeviceDiscoveryAgent(self)
        self.m_deviceDiscoveryAgent.setLowEnergyDiscoveryTimeout(15000)
        self.m_deviceDiscoveryAgent.deviceDiscovered.connect(self.addDevice)
        self.m_deviceDiscoveryAgent.errorOccurred.connect(self.scanError)

        self.m_deviceDiscoveryAgent.finished.connect(self.scanFinished)
        self.m_deviceDiscoveryAgent.canceled.connect(self.scanFinished)
#! [devicediscovery-1]
        if simulator():
            self.m_demoTimer.setSingleShot(True)
            self.m_demoTimer.setInterval(2000)
            self.m_demoTimer.timeout.connect(self.scanFinished)

    @Slot()
    def startSearch(self):
        if is_android or sys.platform == "darwin":
            error_not_nuitka()
            permission = QBluetoothPermission()
            permission.setCommunicationModes(QBluetoothPermission.Access)
            permission_status = qApp.checkPermission(permission)  # noqa: F821
            if permission_status == Qt.PermissionStatus.Undetermined:
                qApp.requestPermission(permission, self, self.startSearch)  # noqa: F82 1
                return
            elif permission_status == Qt.PermissionStatus.Denied:
                return
            elif permission_status == Qt.PermissionStatus.Granted:
                print("[HeartRateGame] Bluetooth Permission Granted")

        self.clearMessages()
        self.m_deviceHandler.setDevice(None)
        self.m_devices.clear()

        self.devicesChanged.emit()

        if simulator():
            self.m_demoTimer.start()
        else:
#! [devicediscovery-2]
            self.m_deviceDiscoveryAgent.start(QBluetoothDeviceDiscoveryAgent.LowEnergyMethod)
#! [devicediscovery-2]
            self.scanningChanged.emit()
        self.info = "Scanning for devices..."

#! [devicediscovery-3]
    @Slot(QBluetoothDeviceInfo)
    def addDevice(self, device):
        # If device is LowEnergy-device, add it to the list
        if device.coreConfigurations() & QBluetoothDeviceInfo.LowEnergyCoreConfiguration:
            self.m_devices.append(DeviceInfo(device))
            self.info = "Low Energy device found. Scanning more..."
#! [devicediscovery-3]
            self.devicesChanged.emit()
#! [devicediscovery-4]
    #...
#! [devicediscovery-4]

    @Slot(QBluetoothDeviceDiscoveryAgent.Error)
    def scanError(self, error):
        if error == QBluetoothDeviceDiscoveryAgent.PoweredOffError:
            self.error = "The Bluetooth adaptor is powered off."
        elif error == QBluetoothDeviceDiscoveryAgent.InputOutputError:
            self.error = "Writing or reading from the device resulted in an error."
        else:
            self.error = "An unknown error has occurred."

    @Slot()
    def scanFinished(self):
        if simulator():
            # Only for testing
            for i in range(5):
                self.m_devices.append(DeviceInfo(QBluetoothDeviceInfo()))

        if self.m_devices:
            self.info = "Scanning done."
        else:
            self.error = "No Low Energy devices found."

        self.scanningChanged.emit()
        self.devicesChanged.emit()

    @Slot(str)
    def connectToService(self, address):
        self.m_deviceDiscoveryAgent.stop()

        currentDevice = None
        for entry in self.m_devices:
            device = entry
            if device and device.deviceAddress == address:
                currentDevice = device
                break

        if currentDevice:
            self.m_deviceHandler.setDevice(currentDevice)

        self.clearMessages()

    @Property(bool, notify=scanningChanged)
    def scanning(self):
        if simulator():
            return self.m_demoTimer.isActive()
        return self.m_deviceDiscoveryAgent.isActive()

    @Property("QVariant", notify=devicesChanged)
    def devices(self):
        return self.m_devices
