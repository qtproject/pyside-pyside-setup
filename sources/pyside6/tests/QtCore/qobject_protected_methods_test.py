#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for QObject protected methods'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject, QThread, SIGNAL


class Dummy(QObject):
    '''Dummy class'''
    pass


class QObjectReceivers(unittest.TestCase):
    '''Test case for QObject.receivers()'''

    def cb(self, *args):
        # Dummy callback
        pass

    def testQObjectReceiversExtern(self):
        # QObject.receivers() - Protected method external access

        obj = Dummy()
        self.assertEqual(obj.receivers(SIGNAL("destroyed()")), 0)

        obj.destroyed.connect(self.cb)
        self.assertEqual(obj.receivers(SIGNAL("destroyed()")), 1)

    def testQThreadReceiversExtern(self):
        # QThread.receivers() - Inherited protected method

        obj = QThread()
        self.assertEqual(obj.receivers(SIGNAL('destroyed()')), 0)
        obj.destroyed.connect(self.cb)
        self.assertEqual(obj.receivers(SIGNAL("destroyed()")), 1)


if __name__ == '__main__':
    unittest.main()
