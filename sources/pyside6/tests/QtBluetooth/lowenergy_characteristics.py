#!/usr/bin/python

#############################################################################
##
## Copyright (C) 2022 The Qt Company Ltd.
## Contact: https://www.qt.io/licensing/
##
## This file is part of the test suite of Qt for Python.
##
## $QT_BEGIN_LICENSE:GPL-EXCEPT$
## Commercial License Usage
## Licensees holding valid commercial Qt licenses may use this file in
## accordance with the commercial license agreement provided with the
## Software or, alternatively, in accordance with the terms contained in
## a written agreement between you and The Qt Company. For licensing terms
## and conditions see https://www.qt.io/terms-conditions. For further
## information use the contact form at https://www.qt.io/contact-us.
##
## GNU General Public License Usage
## Alternatively, this file may be used under the terms of the GNU
## General Public License version 3 as published by the Free Software
## Foundation with exceptions as appearing in the file LICENSE.GPL3-EXCEPT
## included in the packaging of this file. Please review the following
## information to ensure the GNU General Public License requirements will
## be met: https://www.gnu.org/licenses/gpl-3.0.html.
##
## $QT_END_LICENSE$
##
#############################################################################

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
