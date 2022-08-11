# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

"""PySide6 port of the bluetooth/heartrate-server example from Qt v6.x"""

import sys
from enum import Enum

from PySide6.QtBluetooth import (QBluetoothUuid, QLowEnergyAdvertisingData,
                                 QLowEnergyAdvertisingParameters,
                                 QLowEnergyCharacteristic,
                                 QLowEnergyCharacteristicData,
                                 QLowEnergyController,
                                 QLowEnergyDescriptorData,
                                 QLowEnergyServiceData)
from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import QByteArray, QTimer, QLoggingCategory


class ValueChange(Enum):
    VALUE_UP = 1
    VALUE_DOWN = 2


if __name__ == '__main__':
    app = QGuiApplication(sys.argv)
    QLoggingCategory.setFilterRules("qt.bluetooth* = true")

#! [Advertising Data]
    advertising_data = QLowEnergyAdvertisingData()
    advertising_data.setDiscoverability(QLowEnergyAdvertisingData.DiscoverabilityGeneral)
    advertising_data.setIncludePowerLevel(True)
    advertising_data.setLocalName("HeartRateServer")
    advertising_data.setServices([QBluetoothUuid.ServiceClassUuid.HeartRate])
#! [Advertising Data]

#! [Service Data]
    char_data = QLowEnergyCharacteristicData()
    char_data.setUuid(QBluetoothUuid.CharacteristicType.HeartRateMeasurement)
    char_data.setValue(QByteArray(2, 0))
    char_data.setProperties(QLowEnergyCharacteristic.Notify)
    client_config = QLowEnergyDescriptorData(QBluetoothUuid.DescriptorType.ClientCharacteristicConfiguration,
                                             QByteArray(2, 0))
    char_data.addDescriptor(client_config)

    service_data = QLowEnergyServiceData()
    service_data.setType(QLowEnergyServiceData.ServiceTypePrimary)
    service_data.setUuid(QBluetoothUuid.ServiceClassUuid.HeartRate)
    service_data.addCharacteristic(char_data)
#! [Service Data]

#! [Start Advertising]
    le_controller = QLowEnergyController.createPeripheral()
    service = le_controller.addService(service_data)
    le_controller.startAdvertising(QLowEnergyAdvertisingParameters(),
                                   advertising_data, advertising_data)
#! [Start Advertising]

#! [Provide Heartbeat]
    value_change = ValueChange.VALUE_UP
    heartbeat_timer = QTimer()
    current_heart_rate = 60

    def heartbeat_provider():
        global current_heart_rate, value_change, current_heart_rate
        value = QByteArray()
        value.append(chr(0))  # Flags that specify the format of the value.
        value.append(chr(current_heart_rate))  # Actual value.
        characteristic = service.characteristic(QBluetoothUuid.CharacteristicType.HeartRateMeasurement)
        assert(characteristic.isValid())
        # Potentially causes notification.
        service.writeCharacteristic(characteristic, value)
        if current_heart_rate == 60:
            value_change = ValueChange.VALUE_UP
        elif current_heart_rate == 100:
            value_change = ValueChange.VALUE_DOWN
        if value_change == ValueChange.VALUE_UP:
            current_heart_rate += 1
        else:
            current_heart_rate -= 1

    heartbeat_timer.timeout.connect(heartbeat_provider)
    heartbeat_timer.start(1000)
#! [Provide Heartbeat]

    def reconnect():
        service = le_controller.addService(service_data)
        if not service.isNull():
            le_controller.startAdvertising(QLowEnergyAdvertisingParameters(),
                                           advertising_data, advertising_data)

    le_controller.disconnected.connect(reconnect)

    sys.exit(app.exec())
