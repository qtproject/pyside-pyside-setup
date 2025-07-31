# Copyright (C) 2025 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test case for non-QObject.receivers'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths  # noqa: F401
init_test_paths(False)

from helper.usesqapplication import UsesQApplication  # noqa: F401

from PySide6.QtGui import QAction  # noqa: F401


receiver_instances = 0


class Receiver:

    def __init__(self):
        global receiver_instances
        receiver_instances += 1
        self.slot1Triggered = 0
        self.slot2Triggered = 0

    def __del__(self):
        global receiver_instances
        receiver_instances -= 1

    def slot1(self):
        self.slot1Triggered += 1

    def slot2(self):
        self.slot2Triggered += 1


class TestQObjectReceivers(UsesQApplication):
    '''Test case for non-QObject.receivers'''

    @unittest.skipUnless(hasattr(sys, "getrefcount"), f"{sys.implementation.name} has no refcount")
    def testBasic(self):
        '''The test verifies that connections to methods of a non-QObject work
           (TrackingMethodDynamicSlot). Also, despite being stored in the signal manager,
           making connections should not increase references on the receiver or prevent
           the receivers from being deleted, which is achieved using weak reference
           tracking notifications.
           2 connections are used to trigger a corruption caused by multiple weak reference
           notifications (PYSIDE-3148).'''
        action1 = QAction("a1", qApp)  # noqa: F821
        action2 = QAction("a2", qApp)  # noqa: F821
        receiver = Receiver()
        self.assertEqual(receiver_instances, 1)
        base_ref_count = sys.getrefcount(receiver)
        action1.triggered.connect(receiver.slot1)
        action2.triggered.connect(receiver.slot2)
        self.assertEqual(sys.getrefcount(receiver), base_ref_count)
        action1.trigger()
        action2.trigger()
        self.assertEqual(receiver.slot1Triggered, 1)
        self.assertEqual(receiver.slot2Triggered, 1)
        receiver = 0
        self.assertEqual(receiver_instances, 0)


if __name__ == '__main__':
    unittest.main()
