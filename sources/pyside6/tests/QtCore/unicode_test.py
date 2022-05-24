#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Unit tests for QString conversion to/from Python Unicode'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject
from PySide6.QtCore import QByteArray


class UnicodeConversion(unittest.TestCase):
    '''Test case for QString to/from Python Unicode conversion'''

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testSetRegularStringRetrieveUnicode(self):
        # Set regular Python string retrieve unicode
        obj = QObject()
        obj.setObjectName('test')
        self.assertEqual(obj.objectName(), 'test')

    def testSetUnicodeRetrieveUnicode(self):
        # Set Python unicode string and retrieve unicode
        obj = QObject()
        obj.setObjectName('ümlaut')
        self.assertEqual(obj.objectName(), 'ümlaut')


if __name__ == '__main__':
    unittest.main()

