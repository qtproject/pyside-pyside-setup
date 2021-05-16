#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Unit tests for QObject's tr static methods.'''

import gc
import os
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject

#from helper.usesqapplication import UsesQApplication


class QObjectTrTest(unittest.TestCase):
    '''Test case to check if QObject tr static methods could be treated as instance methods.'''

    def setUp(self):
        self.obj = QObject()

    def tearDown(self):
        del self.obj
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()

    def testTrCommonCase(self):
        # Test common case for QObject.tr
        invar1 = 'test1'
        outvar1 = self.obj.tr(invar1)
        invar2 = 'test2'
        outvar2 = self.obj.tr(invar2, 'test comment')
        self.assertEqual((invar1, invar2), (outvar1, outvar2))

    def testTrAsInstanceMethod(self):
        # Test QObject.tr as instance.
        # PYSIDE-1252: This works now as a class method!
        invar1 = 'test1'
        outvar1 = QObject.tr(invar1)
        invar2 = 'test2'
        outvar2 = QObject.tr(invar2, 'test comment')
        self.assertEqual((invar1, invar2), (outvar1, outvar2))


if __name__ == '__main__':
    unittest.main()

