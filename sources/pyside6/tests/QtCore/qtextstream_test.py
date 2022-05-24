# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Unit tests for QTextStream'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QByteArray, QTextStream, QIODevice, QFile


class QTextStreamShiftTest(unittest.TestCase):

    def setUp(self):
        self.ba = QByteArray()
        self.read = QTextStream(self.ba, QIODevice.ReadOnly)
        self.write = QTextStream(self.ba, QIODevice.WriteOnly)

    def testNumber(self):
        '''QTextStream << number'''

        self.write << '4'
        self.write.flush()
        res = self.read.readLine()
        self.assertTrue(isinstance(res, str))
        self.assertEqual(res, '4')


class QTextStreamGetSet(unittest.TestCase):

    def setUp(self):
        self.obj = QTextStream()

    def testDevice(self):
        '''QTextStream get/set Device'''
        device = QFile()
        self.obj.setDevice(device)
        self.assertEqual(device, self.obj.device())
        self.obj.setDevice(None)
        self.assertEqual(None, self.obj.device())


class QTextStreamInitialization(unittest.TestCase):

    def testConstruction(self):
        '''QTextStream construction'''
        obj = QTextStream()

        self.assertEqual(obj.device(), None)
        self.assertEqual(obj.string(), None)

        self.assertTrue(obj.atEnd())
        self.assertEqual(obj.readAll(), '')


class QTextStreamReadLinesFromDevice(unittest.TestCase):

    def _check_data(self, data_set):

        for data, lines in data_set:
            stream = QTextStream(data)

            res = []
            while not stream.atEnd():
                res.append(stream.readLine())

            self.assertEqual(res, lines)

    def testLatin1(self):
        '''QTextStream readLine for simple Latin1 strings'''

        data = []

        data.append((QByteArray(), []))
        data.append((QByteArray(bytes('\n', "UTF-8")), ['']))
        data.append((QByteArray(bytes('\r\n', "UTF-8")), ['']))
        data.append((QByteArray(bytes('ole', "UTF-8")), ['ole']))
        data.append((QByteArray(bytes('ole\n', "UTF-8")), ['ole']))
        data.append((QByteArray(bytes('ole\r\n', "UTF-8")), ['ole']))
        data.append((QByteArray(bytes('ole\r\ndole\r\ndoffen', "UTF-8")), ['ole', 'dole', 'doffen']))

        self._check_data(data)


if __name__ == '__main__':
    unittest.main()
