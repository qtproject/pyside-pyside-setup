#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for QSensor'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtSensors import QSensor, QSensorReading


class QSensorTest(unittest.TestCase):
    def test(self):
        for sensorType in QSensor.sensorTypes():
            identifiers = QSensor.sensorsForType(sensorType)
            values = []
            error = ''
            for identifier in identifiers:
                sensor = QSensor(sensorType, None)
                sensor.setIdentifier(identifier)
                if sensor.connectToBackend():
                    usedIdentifier = identifier
                    reading = sensor.reading()
                    if reading:
                        for i in range(0, reading.valueCount()):
                            values.append(reading.value(i))
                        break
                    else:
                        error = "Unable to obtain reading"
                else:
                    error = "Unable to connect to backend"
            if values:
                print('Sensor ', sensorType, usedIdentifier, values)
            else:
                print(f"{sensorType}: {error}", file=sys.stderr)


if __name__ == '__main__':
    unittest.main()
