#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for QLowEnergyServiceData'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QUuid
from PySide6.QtBluetooth import (QBluetoothUuid, QLowEnergyServiceData,
                                 QLowEnergyDescriptorData,
                                 QLowEnergyCharacteristicData)


class QLowEnergyCharacteristicsTest(unittest.TestCase):

    def testCharacteristics(self):
        uuid = QUuid("11111111-1111-1111-1111-111111111111")
        self.assertFalse(uuid.isNull())

        new_characteristic = QLowEnergyCharacteristicData()
        bluetooth_uuid = QBluetoothUuid(uuid)
        new_characteristic.setUuid(bluetooth_uuid)
        new_characteristic.setValue(b"blabla")
        new_characteristic.setValueLength(6, 20)

        desc = QLowEnergyDescriptorData()
        desc.setUuid(bluetooth_uuid)
        desc.setValue(b"blabla")

        new_characteristic.addDescriptor(desc)
        self.assertTrue(new_characteristic.isValid())

        data = QLowEnergyServiceData()
        data.addCharacteristic(new_characteristic)

        characteristics = data.characteristics()
        self.assertEqual(len(characteristics), 1)

        self.assertEqual(characteristics[0].uuid(), bluetooth_uuid)


if __name__ == '__main__':
    unittest.main()
