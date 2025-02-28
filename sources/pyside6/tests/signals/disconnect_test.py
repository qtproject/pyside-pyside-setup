# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
from __future__ import annotations

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(True)

from PySide6.QtCore import QObject, Signal, Slot, SIGNAL, SLOT
from testbinding import TestObject


class Sender(QObject):
    bar = Signal()


class Receiver(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.called = 0

    @Slot()
    def receiver(self):
        self.called += 1


class TestDisconnect(unittest.TestCase):
    def theSlot1(self):
        self.called1 = True

    def theSlot2(self):
        self.called2 = True

    def testIt(self):
        self.called1 = False
        self.called2 = False
        s = Sender()
        s.bar.connect(self.theSlot1)
        s.bar.connect(self.theSlot2)
        s.bar.emit()
        self.assertTrue(self.called1)
        self.assertTrue(self.called2)

        self.called1 = False
        self.called2 = False
        self.assertTrue(s.bar.disconnect())  # Disconnect sender
        s.bar.emit()
        self.assertFalse(self.called1)
        self.assertFalse(self.called2)

    def testCallable(self):
        s = Sender()
        r = Receiver()
        s.bar.connect(r.receiver)
        s.bar.emit()
        self.assertEqual(r.called, 1)
        self.assertTrue(s.bar.disconnect(r.receiver))
        s.bar.emit()
        self.assertEqual(r.called, 1)

    def testStringBased(self):
        s = Sender()
        r = Receiver()
        QObject.connect(s, SIGNAL("bar()"), r, SLOT("receiver()"))
        s.bar.emit()
        self.assertEqual(r.called, 1)
        self.assertTrue(QObject.disconnect(s, SIGNAL("bar()"), r, SLOT("receiver()")))
        s.bar.emit()
        self.assertEqual(r.called, 1)

    def testMixStringBasedCallable(self):
        """PYSIDE-3020, Disconnect a string-based connection by passing a callable."""
        s = Sender()
        r = Receiver()
        QObject.connect(s, SIGNAL("bar()"), r, SLOT("receiver()"))
        s.bar.emit()
        self.assertEqual(r.called, 1)
        self.assertTrue(s.bar.disconnect(r.receiver))
        s.bar.emit()
        self.assertEqual(r.called, 1)

    def testMixCallableStringBased(self):
        """PYSIDE-3020, test vice versa."""
        s = Sender()
        r = Receiver()
        s.bar.connect(r.receiver)
        s.bar.emit()
        self.assertEqual(r.called, 1)
        self.assertTrue(QObject.disconnect(s, SIGNAL("bar()"), r, SLOT("receiver()")))
        s.bar.emit()
        self.assertEqual(r.called, 1)

    def testMetaMethod(self):
        s = Sender()
        r = Receiver()
        sender_mo = s.metaObject()
        signal_index = sender_mo.indexOfMethod("bar()")
        self.assertTrue(signal_index != -1)
        signal_method = sender_mo.method(signal_index)
        receiver_mo = r.metaObject()
        slot_index = receiver_mo.indexOfMethod("receiver()")
        self.assertTrue(slot_index != -1)
        slot_method = receiver_mo.method(slot_index)
        conn_id = QObject.connect(s, signal_method, r, slot_method)
        self.assertTrue(conn_id)
        s.bar.emit()
        self.assertEqual(r.called, 1)
        self.assertTrue(QObject.disconnect(s, signal_method, r, slot_method))
        s.bar.emit()
        self.assertEqual(r.called, 1)

    def testDuringCallback(self):
        """ Test to see if the C++ object for a connection is accessed after the
        method returns.  This causes a segfault if the memory that was used by the
        C++ object has been reused. """

        self.called = False
        obj = TestObject(0)

        def callback():
            obj.signalWithDefaultValue.disconnect(callback)

            # Connect more callbacks to try to overwrite memory
            for i in range(1000):
                obj.signalWithDefaultValue.connect(lambda: None)

            self.called = True

            # A non-None return value is needed
            return True
        obj.signalWithDefaultValue.connect(callback)
        obj.signalWithDefaultValue.emit()
        self.assertTrue(self.called)


if __name__ == '__main__':
    unittest.main()
