#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for QCbor'''

import gc
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import (QByteArray, QCborStreamReader, QCborStreamWriter,
    QCborTag, QCborValue)


class TestCbor(unittest.TestCase):
    def testReader(self):
        ba = QByteArray()
        writer = QCborStreamWriter(ba)
        writer.append(42)
        del writer
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        self.assertTrue(not ba.isEmpty())
        reader = QCborStreamReader(ba)
        self.assertTrue(reader.hasNext())
        value = reader.toInteger()
        self.assertEqual(value, 42)

    def testReader(self):
        ba = QByteArray()
        writer = QCborStreamWriter(ba)
        writer.append("hello")
        del writer
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        self.assertTrue(not ba.isEmpty())
        reader = QCborStreamReader(ba)
        self.assertTrue(reader.hasNext())
        if (reader.isByteArray()):  # Python 2
            value = reader.readByteArray()
            self.assertTrue(value)
            self.assertEqual(value.data, "hello")
        else:
            self.assertTrue(reader.isString())
            value = reader.readString()
            self.assertTrue(value)
            self.assertEqual(value.data, "hello")

    def testValue(self):
        value = QCborValue('hello')
        self.assertTrue(value.isString())
        self.assertEqual(value.toString(), 'hello')
        if sys.pyside63_option_python_enum:
            # PYSIDE-1735: Undefined enums are not possible
            return
        tag = value.tag(QCborTag(32))
        self.assertEqual(int(tag), 32)


if __name__ == '__main__':
    unittest.main()
