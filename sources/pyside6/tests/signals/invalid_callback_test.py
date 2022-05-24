# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for passing invalid callbacks to QObject.connect'''

import gc
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject, SIGNAL


class InvalidCallback(unittest.TestCase):
    '''Test case for passing an invalid callback to QObject.connect'''

    def setUp(self):
        # Acquire resources
        self.obj = QObject()

    def tearDown(self):
        # Release resources
        try:
            del self.obj
        except AttributeError:
            pass
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()

    def testIntegerCb(self):
        # Test passing an int as callback to QObject.connect
        self.assertRaises(TypeError, QObject.connect, self.obj,
                            SIGNAL('destroyed()'), 42)


if __name__ == '__main__':
    unittest.main()

