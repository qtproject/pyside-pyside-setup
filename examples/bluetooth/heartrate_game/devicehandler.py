# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import struct

from enum import IntEnum

from PySide6.QtBluetooth import (QLowEnergyCharacteristic,
                                 QLowEnergyController,
                                 QLowEnergyDescriptor,
                                 QLowEnergyService,
                                 QBluetoothUuid)
from PySide6.QtQml import QmlNamedElement, QmlUncreatable
from PySide6.QtCore import (QByteArray, QDateTime, QRandomGenerator, QTimer,
                            Property, Signal, Slot, QEnum)

from bluetoothbaseclass import BluetoothBaseClass
from heartrate_global import simulator


# To be used on the @QmlElement decorator
# (QML_IMPORT_MINOR_VERSION is optional)
QML_IMPORT_NAME = "Shared"
QML_IMPORT_MAJOR_VERSION = 1


@QmlNamedElement("AddressType")
@QmlUncreatable("Enum is not a type")
class DeviceHandler(BluetoothBaseClass):

    @QEnum
    class AddressType(IntEnum):
        PUBLIC_ADDRESS = 1
        RANDOM_ADDRESS = 2

    measuringChanged = Signal()
    aliveChanged = Signal()
    statsChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.m_control = None
        self.m_service = None
        self.m_notificationDesc = QLowEnergyDescriptor()
        self.m_currentDevice = None

        self.m_foundHeartRateService = False
        self.m_measuring = False
        self.m_currentValue = 0
        self.m_min = 0
        self.m_max = 0
        self.m_sum = 0
        self.m_avg = 0.0
        self.m_calories = 0.0

        self.m_start = QDateTime()
        self.m_stop = QDateTime()

        self.m_measurements = []
        self.m_addressType = QLowEnergyController.PublicAddress

        self.m_demoTimer = QTimer()

        if simulator:
            self.m_demoTimer.setSingleShot(False)
            self.m_demoTimer.setInterval(2000)
            self.m_demoTimer.timeout.connect(self.updateDemoHR)
            self.m_demoTimer.start()
            self.updateDemoHR()

    @Property(int)
    def addressType(self):
        if self.m_addressType == QLowEnergyController.RandomAddress:
            return DeviceHandler.AddressType.RANDOM_ADDRESS
        return DeviceHandler.AddressType.PUBLIC_ADDRESS

    @addressType.setter
    def addressType(self, type):
        if type == DeviceHandler.AddressType.PUBLIC_ADDRESS:
            self.m_addressType = QLowEnergyController.PublicAddress
        elif type == DeviceHandler.AddressType.RANDOM_ADDRESS:
            self.m_addressType = QLowEnergyController.RandomAddress

    @Slot(QLowEnergyController.Error)
    def controllerErrorOccurred(self, device):
        self.error = "Cannot connect to remote device."

    @Slot()
    def controllerConnected(self):
        self.info = "Controller connected. Search services..."
        self.m_control.discoverServices()

    @Slot()
    def controllerDisconnected(self):
        self.error = "LowEnergy controller disconnected"

    def setDevice(self, device):
        self.clearMessages()
        self.m_currentDevice = device

        if simulator:
            self.info = "Demo device connected."
            return

        # Disconnect and delete old connection
        if self.m_control:
            self.m_control.disconnectFromDevice()
            m_control = None

        # Create new controller and connect it if device available
        if self.m_currentDevice:

            # Make connections
#! [Connect-Signals-1]
            self.m_control = QLowEnergyController.createCentral(self.m_currentDevice.getDevice(), self)
#! [Connect-Signals-1]
            self.m_control.setRemoteAddressType(self.m_addressType)
#! [Connect-Signals-2]

            m_control.serviceDiscovered.connect(self.serviceDiscovered)
            m_control.discoveryFinished.connect(self.serviceScanDone)

            self.m_control.errorOccurred.connect(self.controllerErrorOccurred)
            self.m_control.connected.connect(self.controllerConnected)
            self.m_control.disconnected.connect(self.controllerDisconnected)

            # Connect
            self.m_control.connectToDevice()
#! [Connect-Signals-2]

    @Slot()
    def startMeasurement(self):
        if self.alive:
            self.m_start = QDateTime.currentDateTime()
            self.m_min = 0
            self.m_max = 0
            self.m_avg = 0
            self.m_sum = 0
            self.m_calories = 0.0
            self.m_measuring = True
            self.m_measurements.clear()
            self.measuringChanged.emit()

    @Slot()
    def stopMeasurement(self):
        self.m_measuring = False
        self.measuringChanged.emit()

#! [Filter HeartRate service 1]
    @Slot(QBluetoothUuid)
    def serviceDiscovered(self, gatt):
        if gatt == QBluetoothUuid(QBluetoothUuid.ServiceClassUuid.HeartRate):
            self.info = "Heart Rate service discovered. Waiting for service scan to be done..."
            self.m_foundHeartRateService = True

#! [Filter HeartRate service 1]

    @Slot()
    def serviceScanDone(self):
        self.info = "Service scan done."

        # Delete old service if available
        if self.m_service:
            self.m_service = None

#! [Filter HeartRate service 2]
        # If heartRateService found, create new service
        if self.m_foundHeartRateService:
            self.m_service = self.m_control.createServiceObject(QBluetoothUuid(QBluetoothUuid.ServiceClassUuid.HeartRate), self)

        if self.m_service:
            self.m_service.stateChanged.connect(self.serviceStateChanged)
            self.m_service.characteristicChanged.connect(self.updateHeartRateValue)
            self.m_service.descriptorWritten.connect(self.confirmedDescriptorWrite)
            self.m_service.discoverDetails()
        else:
            self.error = "Heart Rate Service not found."
#! [Filter HeartRate service 2]

# Service functions
#! [Find HRM characteristic]
    @Slot(QLowEnergyService.ServiceState)
    def serviceStateChanged(self, switch):
        if switch == QLowEnergyService.RemoteServiceDiscovering:
            self.setInfo(tr("Discovering services..."))
        elif switch == QLowEnergyService.RemoteServiceDiscovered:
            self.setInfo(tr("Service discovered."))
            hrChar = m_service.characteristic(QBluetoothUuid(QBluetoothUuid.CharacteristicType.HeartRateMeasurement))
            if hrChar.isValid():
                self.m_notificationDesc = hrChar.descriptor(QBluetoothUuid.DescriptorType.ClientCharacteristicConfiguration)
                if self.m_notificationDesc.isValid():
                    self.m_service.writeDescriptor(m_notificationDesc,
                                                   QByteArray.fromHex(b"0100"))
            else:
                self.error = "HR Data not found."
        self.aliveChanged.emit()
#! [Find HRM characteristic]

#! [Reading value]
    @Slot(QLowEnergyCharacteristic, QByteArray)
    def updateHeartRateValue(self, c, value):
        # ignore any other characteristic change. Shouldn't really happen though
        if c.uuid() != QBluetoothUuid(QBluetoothUuid.CharacteristicType.HeartRateMeasurement):
            return

        data = value.data()
        flags = int(data[0])
        # Heart Rate
        hrvalue = 0
        if flags & 0x1:  # HR 16 bit little endian? otherwise 8 bit
            hrvalue = struct.unpack("<H", data[1:3])
        else:
            hrvalue = struct.unpack("B", data[1:2])

        self.addMeasurement(hrvalue)

#! [Reading value]
    @Slot()
    def updateDemoHR(self):
        randomValue = 0
        if self.m_currentValue < 30:  # Initial value
            randomValue = 55 + QRandomGenerator.global_().bounded(30)
        elif not self.m_measuring:  # Value when relax
            random = QRandomGenerator.global_().bounded(5)
            randomValue = self.m_currentValue - 2 + random
            randomValue = max(min(randomValue, 55), 75)
        else:  # Measuring
            random = QRandomGenerator.global_().bounded(10)
            randomValue = self.m_currentValue + random - 2

        self.addMeasurement(randomValue)

    @Slot(QLowEnergyCharacteristic, QByteArray)
    def confirmedDescriptorWrite(self, d, value):
        if (d.isValid() and d == self.m_notificationDesc
            and value == QByteArray.fromHex(b"0000")):
            # disabled notifications . assume disconnect intent
            self.m_control.disconnectFromDevice()
            self.m_service = None

    @Slot()
    def disconnectService(self):
        self.m_foundHeartRateService = False

        # disable notifications
        if (self.m_notificationDesc.isValid() and self.m_service
            and self.m_notificationDesc.value() == QByteArray.fromHex(b"0100")):
            self.m_service.writeDescriptor(self.m_notificationDesc,
                                           QByteArray.fromHex(b"0000"))
        else:
            if self.m_control:
                self.m_control.disconnectFromDevice()
            self.m_service = None

    @Property(bool, notify=measuringChanged)
    def measuring(self):
        return self.m_measuring

    @Property(bool, notify=aliveChanged)
    def alive(self):
        if simulator:
            return True
        if self.m_service:
            return self.m_service.state() == QLowEnergyService.RemoteServiceDiscovered
        return False

    @Property(int, notify=statsChanged)
    def hr(self):
        return self.m_currentValue

    @Property(int, notify=statsChanged)
    def time(self):
        return self.m_start.secsTo(self.m_stop)

    @Property(int, notify=statsChanged)
    def maxHR(self):
        return self.m_max

    @Property(int, notify=statsChanged)
    def minHR(self):
        return self.m_min

    @Property(float, notify=statsChanged)
    def average(self):
        return self.m_avg

    @Property(float, notify=statsChanged)
    def calories(self):
        return self.m_calories

    def addMeasurement(self, value):
        self.m_currentValue = value

        # If measuring and value is appropriate
        if self.m_measuring and value > 30 and value < 250:
            self.m_stop = QDateTime.currentDateTime()
            self.m_measurements.append(value)

            self.m_min = value if self.m_min == 0 else min(value, self.m_min)
            self.m_max = max(value, self.m_max)
            self.m_sum += value
            self.m_avg = float(self.m_sum) / len(self.m_measurements)
            self.m_calories = ((-55.0969 + (0.6309 * self.m_avg) + (0.1988 * 94)
                               + (0.2017 * 24)) / 4.184) * 60 * self.time / 3600

        self.statsChanged.emit()
