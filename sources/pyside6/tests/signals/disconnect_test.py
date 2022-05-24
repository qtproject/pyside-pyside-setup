# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(True)

from PySide6.QtCore import QObject, Signal
from testbinding import TestObject


class Foo(QObject):
    bar = Signal()


class TestDisconnect(unittest.TestCase):
    def theSlot1(self):
        self.called1 = True

    def theSlot2(self):
        self.called2 = True

    def testIt(self):
        self.called1 = False
        self.called2 = False
        f = Foo()
        f.bar.connect(self.theSlot1)
        f.bar.connect(self.theSlot2)
        f.bar.emit()
        self.assertTrue(self.called1)
        self.assertTrue(self.called2)

        self.called1 = False
        self.called2 = False
        f.bar.disconnect()
        f.bar.emit()
        self.assertFalse(self.called1)
        self.assertFalse(self.called2)

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
