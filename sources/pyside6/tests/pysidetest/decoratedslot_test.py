#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(True)

from PySide6.QtCore import QObject
from testbinding import TestObject


class Receiver(QObject):
    def __init__(self):
        super().__init__()
        self.called = False

    def ReceiverDecorator(func):
        def decoratedFunction(self, *args, **kw):
            func(self, *args, **kw)
        return decoratedFunction

    # This method with the same name of the internal decorated function
    # is here to test the binding capabilities.
    def decoratedFunction(self):
        pass

    @ReceiverDecorator
    def slot(self):
        self.called = True


class DecoratedSlotTest(unittest.TestCase):

    def testCallingOfDecoratedSlot(self):
        obj = TestObject(0)
        receiver = Receiver()
        obj.staticMethodDouble.connect(receiver.slot)
        obj.emitStaticMethodDoubleSignal()
        self.assertTrue(receiver.called)


if __name__ == '__main__':
    unittest.main()

