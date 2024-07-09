#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
from __future__ import annotations

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
        self.assertTrue(obj.receivers(SIGNAL("destroyed()")) > 0)

    def testQThreadReceiversExtern(self):
        # QThread.receivers() - Inherited protected method

        obj = QThread()
        old_count = obj.receivers(SIGNAL('destroyed()'))
        obj.destroyed.connect(self.cb)
        self.assertTrue(obj.receivers(SIGNAL("destroyed()")) > old_count)


if __name__ == '__main__':
    unittest.main()
