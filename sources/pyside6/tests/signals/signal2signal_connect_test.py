# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

''' Test case for signal to signal connections.'''

import gc
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject, Signal


class Sender(QObject):

    mysignal_int = Signal(int)
    mysignal_int_int = Signal(int, int)
    mysignal_string = Signal(str)


class Forwarder(Sender):

    forward = Signal()
    forward_qobject = Signal(QObject)


def cute_slot():
    pass


class TestSignal2SignalConnect(unittest.TestCase):
    '''Test case for signal to signal connections'''

    def setUp(self):
        # Set up the basic resources needed
        self.sender = Sender()
        self.forwarder = Forwarder()
        self.args = None
        self.called = False

    def tearDown(self):
        # Delete used resources
        try:
            del self.sender
        except:  # noqa: E722
            pass
        try:
            del self.forwarder
        except:  # noqa: E722
            pass
        del self.args
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()

    def callback_noargs(self):
        # Default callback without arguments
        self.called = True

    def callback_args(self, *args):
        # Default callback with arguments
        if args == self.args:
            self.called = True
        else:
            raise TypeError("Invalid arguments")

    def callback_qobject(self, *args):
        # Default callback for QObject as argument
        if args[0].objectName() == self.args[0]:
            self.called = True
        else:
            raise TypeError("Invalid arguments")

    def testSignalWithoutArguments(self):
        self.sender.destroyed.connect(self.forwarder.forward)
        self.forwarder.forward.connect(self.callback_noargs)
        del self.sender
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        self.assertTrue(self.called)

    def testSignalWithOnePrimitiveTypeArgument(self):
        self.sender.mysignal_int.connect(self.forwarder.mysignal_int)
        self.forwarder.mysignal_int.connect(self.callback_args)
        self.args = (19,)
        self.sender.mysignal_int.emit(*self.args)
        self.assertTrue(self.called)

    def testSignalWithMultiplePrimitiveTypeArguments(self):
        self.sender.mysignal_int_int.connect(self.forwarder.mysignal_int_int)
        self.forwarder.mysignal_int_int.connect(self.callback_args)
        self.args = (23, 29)
        self.sender.mysignal_int_int.emit(*self.args)
        self.assertTrue(self.called)

    def testSignalWithOneStringArgument(self):
        self.sender.mysignal_string.connect(self.forwarder.mysignal_string)
        self.forwarder.mysignal_string.connect(self.callback_args)
        self.args = ('myargument',)
        self.sender.mysignal_string.emit(*self.args)
        self.assertTrue(self.called)

    def testSignalWithOneQObjectArgument(self):
        self.sender.destroyed.connect(self.forwarder.forward_qobject)
        self.forwarder.forward_qobject.connect(self.callback_qobject)

        obj_name = 'sender'
        self.sender.setObjectName(obj_name)
        self.args = (obj_name, )
        del self.sender
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        self.assertTrue(self.called)


if __name__ == '__main__':
    unittest.main()
