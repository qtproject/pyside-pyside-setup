#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for QString'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject


class QStringConstructor(unittest.TestCase):
    '''Test case for QString constructors'''

    def testQStringDefault(self):
        obj = QObject()
        obj.setObjectName('foo')
        self.assertEqual(obj.objectName(), 'foo')
        obj.setObjectName('áâãà')
        self.assertEqual(obj.objectName(), 'áâãà')
        obj.setObjectName('A\x00B')
        self.assertEqual(obj.objectName(), 'A\x00B')
        obj.setObjectName('ä\x00B')
        self.assertEqual(obj.objectName(), 'ä\x00B')
        obj.setObjectName(None)
        self.assertEqual(obj.objectName(), '')


if __name__ == '__main__':
    unittest.main()
