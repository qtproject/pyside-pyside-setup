# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtCore import QObject, Property, Signal
from PySide6.QtBluetooth import QLowEnergyCharacteristic, QBluetoothUuid


class CharacteristicInfo(QObject):

    characteristic_changed = Signal()

    def __init__(self, characteristic=None) -> None:
        super().__init__()
        self._characteristic = characteristic

    @Property(str, notify=characteristic_changed)
    def characteristic_name(self):
        if not self.characteristic:
            raise Exception("characteristic unset")
        name = self.characteristic.name()
        if name:
            return name

        for descriptor in self.characteristic.descriptors():
            if descriptor.type() == QBluetoothUuid.DescriptorType.CharacteristicUserDescription:
                name = descriptor.value()
                break

        if not name:
            name = "Unknown"

        return name

    @Property(str, notify=characteristic_changed)
    def characteristic_uuid(self):
        uuid = self.characteristic.uuid()
        result16, success16 = uuid.toUInt16()
        if success16:
            return f"0x{result16:x}"

        result32, sucess32 = uuid.toUInt32()
        if sucess32:
            return f"0x{result32:x}"

        return uuid.toString().replace('{', '').replace('}', '')

    @Property(str, notify=characteristic_changed)
    def characteristic_value(self):
        # Show raw string first and hex value below
        a = self.characteristic.value()
        if not a:
            return "<none>"

        result = f"{str(a)}\n{str(a.toHex())}"
        return result

    @Property(str, notify=characteristic_changed)
    def characteristic_permission(self):
        properties = "( "
        permission = self.characteristic.properties()
        if (permission & QLowEnergyCharacteristic.Read):
            properties += " Read"
        if (permission & QLowEnergyCharacteristic.Write):
            properties += " Write"
        if (permission & QLowEnergyCharacteristic.Notify):
            properties += " Notify"
        if (permission & QLowEnergyCharacteristic.Indicate):
            properties += " Indicate"
        if (permission & QLowEnergyCharacteristic.ExtendedProperty):
            properties += " ExtendedProperty"
        if (permission & QLowEnergyCharacteristic.Broadcasting):
            properties += " Broadcast"
        if (permission & QLowEnergyCharacteristic.WriteNoResponse):
            properties += " WriteNoResp"
        if (permission & QLowEnergyCharacteristic.WriteSigned):
            properties += " WriteSigned"
        properties += " )"
        return properties

    @property
    def characteristic(self):
        return self._characteristic

    @characteristic.setter
    def characteristic(self, characteristic):
        self._characteristic = characteristic
        self.characteristic_changed.emit()
