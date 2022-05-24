#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for QByteArray concatenation with '+' operator'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QByteArray


class QByteArrayConcatenationOperatorTest(unittest.TestCase):
    '''Test cases for QByteArray concatenation with '+' operator'''

    def testConcatQByteArrayAndPythonString(self):
        # Test concatenation of a QByteArray with a Python bytes, in this order
        qba = QByteArray(bytes('foo', "UTF-8"))
        result = qba + bytes('\x00bar', "UTF-8")
        self.assertEqual(type(result), QByteArray)
        self.assertEqual(result, bytes('foo\x00bar', "UTF-8"))

    def testConcatPythonStringAndQByteArray(self):
        # Test concatenation of a Python bytes with a QByteArray, in this order
        concat_python_string_add_qbytearray_worked = True
        qba = QByteArray(bytes('foo', "UTF-8"))
        result = bytes('bar\x00', "UTF-8") + qba
        self.assertEqual(type(result), QByteArray)
        self.assertEqual(result, bytes('bar\x00foo', "UTF-8"))


if __name__ == '__main__':
    unittest.main()

