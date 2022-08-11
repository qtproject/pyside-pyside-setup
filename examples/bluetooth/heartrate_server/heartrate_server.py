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
