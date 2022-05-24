#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for QSerialPort'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtSerialPort import QSerialPort, QSerialPortInfo
from PySide6.QtCore import QIODevice


class QSerialPortTest(unittest.TestCase):
    def testDefaultConstructedPort(self):
        serialPort = QSerialPort()

        self.assertEqual(serialPort.error(), QSerialPort.NoError)
        self.assertTrue(not serialPort.errorString() == "")

        # properties
        defaultBaudRate = QSerialPort.Baud9600
        self.assertEqual(serialPort.baudRate(), defaultBaudRate)
        self.assertEqual(serialPort.baudRate(QSerialPort.Input), defaultBaudRate)
        self.assertEqual(serialPort.baudRate(QSerialPort.Output), defaultBaudRate)
        self.assertEqual(serialPort.dataBits(), QSerialPort.Data8)
        self.assertEqual(serialPort.parity(), QSerialPort.NoParity)
        self.assertEqual(serialPort.stopBits(), QSerialPort.OneStop)
        self.assertEqual(serialPort.flowControl(), QSerialPort.NoFlowControl)

        self.assertEqual(serialPort.pinoutSignals(), QSerialPort.NoSignal)
        self.assertEqual(serialPort.isRequestToSend(), False)
        self.assertEqual(serialPort.isDataTerminalReady(), False)

        # QIODevice
        self.assertEqual(serialPort.openMode(), QIODevice.NotOpen)
        self.assertTrue(not serialPort.isOpen())
        self.assertTrue(not serialPort.isReadable())
        self.assertTrue(not serialPort.isWritable())
        self.assertTrue(serialPort.isSequential())
        self.assertEqual(serialPort.canReadLine(), False)
        self.assertEqual(serialPort.pos(), 0)
        self.assertEqual(serialPort.size(), 0)
        self.assertTrue(serialPort.atEnd())
        self.assertEqual(serialPort.bytesAvailable(), 0)
        self.assertEqual(serialPort.bytesToWrite(), 0)

    def testOpenExisting(self):
        allportinfos = QSerialPortInfo.availablePorts()
        for portinfo in allportinfos:
            serialPort = QSerialPort(portinfo)
            self.assertEqual(serialPort.portName(), portinfo.portName())


class QSerialPortInfoTest(unittest.TestCase):
    def test_available_ports(self):
        allportinfos = QSerialPortInfo.availablePorts()
        for portinfo in allportinfos:
            portinfo.description()
            portinfo.hasProductIdentifier()
            portinfo.hasVendorIdentifier()
            portinfo.isNull()


if __name__ == '__main__':
    unittest.main()
