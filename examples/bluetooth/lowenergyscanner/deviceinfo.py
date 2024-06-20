# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

import sys

from PySide6.QtCore import QObject, Property, Signal
from PySide6.QtBluetooth import QBluetoothDeviceInfo


class DeviceInfo(QObject):

    device_changed = Signal()

    def __init__(self, d: QBluetoothDeviceInfo = None) -> None:
        super().__init__()
        self._device = d

    @Property(str, notify=device_changed)
    def device_name(self):
        return self._device.name()

    @Property(str, notify=device_changed)
    def device_address(self):
        if sys.platform == "darwin":
            return self._device.deviceUuid().toString()

        return self._device.address().toString()

    def get_device(self):
        return self._device

    def set_device(self, device):
        self._device = device
        self.device_changed.emit()
