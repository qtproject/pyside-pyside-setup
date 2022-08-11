#############################################################################
##
## Copyright (C) 2022 The Qt Company Ltd.
## Contact: https://www.qt.io/licensing/
##
## This file is part of the Qt for Python examples of the Qt Toolkit.
##
## $QT_BEGIN_LICENSE:BSD$
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of The Qt Company Ltd nor the names of its
##     contributors may be used to endorse or promote products derived
##     from this software without specific prior written permission.
##
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
## $QT_END_LICENSE$
##
#############################################################################

from PySide6.QtBluetooth import (QBluetoothDeviceDiscoveryAgent,
                                 QBluetoothDeviceInfo)
from PySide6.QtQml import QmlElement
from PySide6.QtCore import QTimer, Property, Signal, Slot

from bluetoothbaseclass import BluetoothBaseClass
from deviceinfo import DeviceInfo
from heartrate_global import simulator

# To be used on the @QmlElement decorator
# (QML_IMPORT_MINOR_VERSION is optional)
QML_IMPORT_NAME = "Shared"
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
        if simulator:
            self.m_demoTimer.setSingleShot(True)
            self.m_demoTimer.setInterval(2000)
            self.m_demoTimer.timeout.connect(self.scanFinished)

    @Slot()
    def startSearch(self):
        self.clearMessages()
        self.m_deviceHandler.setDevice(None)
        self.m_devices.clear()

        self.devicesChanged.emit()

        if simulator:
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
        if simulator:
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
        if simulator:
            return self.m_demoTimer.isActive()
        return self.m_deviceDiscoveryAgent.isActive()

    @Property("QVariant", notify=devicesChanged)
    def devices(self):
        return self.m_devices
