# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

import sys

from PySide6.QtCore import QObject, Property, Signal

from heartrate_global import simulator


class DeviceInfo(QObject):

    deviceChanged = Signal()

    def __init__(self, device):
        super().__init__()
        self.m_device = device

    def device(self):
        return self.m_device

    def setDevice(self, device):
        self.m_device = device
        self.deviceChanged.emit()

    @Property(str, notify=deviceChanged)
    def deviceName(self):
        if simulator():
            return "Demo device"
        return self.m_device.name()

    @Property(str, notify=deviceChanged)
    def deviceAddress(self):
        if simulator():
            return "00:11:22:33:44:55"
        if sys.platform == "Darwin":  # workaround for Core Bluetooth:
            return self.m_device.deviceUuid().toString()
        return self.m_device.address().toString()
