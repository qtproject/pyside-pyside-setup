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

from PySide6.QtCore import QObject, SIGNAL


def cute_slot():
    pass


class TestSignal2SignalConnect(unittest.TestCase):
    '''Test case for signal to signal connections'''

    def setUp(self):
        # Set up the basic resources needed
        self.sender = QObject()
        self.forwarder = QObject()
        self.args = None
        self.called = False

    def tearDown(self):
        # Delete used resources
        try:
            del self.sender
        except:
            pass
        try:
            del self.forwarder
        except:
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
        QObject.connect(self.sender, SIGNAL("destroyed()"),
                        self.forwarder, SIGNAL("forward()"))
        QObject.connect(self.forwarder, SIGNAL("forward()"),
                        self.callback_noargs)
        del self.sender
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        self.assertTrue(self.called)

    def testSignalWithOnePrimitiveTypeArgument(self):
        QObject.connect(self.sender, SIGNAL("mysignal(int)"),
                        self.forwarder, SIGNAL("mysignal(int)"))
        QObject.connect(self.forwarder, SIGNAL("mysignal(int)"),
                        self.callback_args)
        self.args = (19,)
        self.sender.emit(SIGNAL('mysignal(int)'), *self.args)
        self.assertTrue(self.called)

    def testSignalWithMultiplePrimitiveTypeArguments(self):
        QObject.connect(self.sender, SIGNAL("mysignal(int,int)"),
                        self.forwarder, SIGNAL("mysignal(int,int)"))
        QObject.connect(self.forwarder, SIGNAL("mysignal(int,int)"),
                        self.callback_args)
        self.args = (23, 29)
        self.sender.emit(SIGNAL('mysignal(int,int)'), *self.args)
        self.assertTrue(self.called)

    def testSignalWithOneStringArgument(self):
        QObject.connect(self.sender, SIGNAL("mysignal(QString)"),
                        self.forwarder, SIGNAL("mysignal(QString)"))
        QObject.connect(self.forwarder, SIGNAL("mysignal(QString)"),
                        self.callback_args)
        self.args = ('myargument',)
        self.sender.emit(SIGNAL('mysignal(QString)'), *self.args)
        self.assertTrue(self.called)

    def testSignalWithOneQObjectArgument(self):
        QObject.connect(self.sender, SIGNAL('destroyed(QObject*)'),
                        self.forwarder, SIGNAL('forward(QObject*)'))
        QObject.connect(self.forwarder, SIGNAL('forward(QObject*)'),
                        self.callback_qobject)

        obj_name = 'sender'
        self.sender.setObjectName(obj_name)
        self.args = (obj_name, )
        del self.sender
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        self.assertTrue(self.called)


if __name__ == '__main__':
    unittest.main()


