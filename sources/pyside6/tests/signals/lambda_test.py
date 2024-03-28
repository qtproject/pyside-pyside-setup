#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Connecting lambda to signals'''

import os
import sys
import unittest
import weakref

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QCoreApplication, QObject, Signal, SIGNAL, QProcess

from helper.usesqapplication import UsesQApplication


class Sender(QObject):
    void_signal = Signal()
    int_signal = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._delayed_int = 0

    def emit_void(self):
        self.void_signal.emit()

    def emit_int(self, v):
        self.int_signal.emit(v)


class Receiver(QObject):

    def __init__(self, *args):
        super().__init__(*args)


class BasicCase(unittest.TestCase):

    def testSimplePythonSignalNoArgs(self):
        # Connecting a lambda to a simple python signal without arguments
        receiver = Receiver()
        sender = Sender()
        sender.void_signal.connect(lambda: setattr(receiver, 'called', True))
        sender.emit_void()
        self.assertTrue(receiver.called)

    def testSimplePythonSignal(self):
        # Connecting a lambda to a simple python signal witharguments
        receiver = Receiver()
        sender = Sender()
        arg = 42
        sender.int_signal.connect(lambda x: setattr(receiver, 'arg', arg))
        sender.emit_int(arg)
        self.assertEqual(receiver.arg, arg)

    def testSimplePythonSignalNoArgsString(self):
        # Connecting a lambda to a simple python signal without arguments
        receiver = Receiver()
        sender = Sender()
        QObject.connect(sender, SIGNAL('void_signal()'),
                        lambda: setattr(receiver, 'called', True))
        sender.emit_void()
        self.assertTrue(receiver.called)

    def testSimplePythonSignalString(self):
        # Connecting a lambda to a simple python signal witharguments
        receiver = Receiver()
        sender = Sender()
        arg = 42
        QObject.connect(sender, SIGNAL('int_signal(int)'),
                        lambda x: setattr(receiver, 'arg', arg))
        sender.emit_int(arg)
        self.assertEqual(receiver.arg, arg)


class QtSigLambda(UsesQApplication):

    qapplication = True

    def testWithArgs(self):
        '''Connecting a lambda to a signal with and without arguments'''
        proc = QProcess()
        dummy = Receiver()
        proc.started.connect(lambda: setattr(dummy, 'called', True))
        proc.finished.connect(lambda x: setattr(dummy, 'exit_code', x))

        proc.start(sys.executable, ['-c', '""'])
        self.assertTrue(proc.waitForStarted())
        self.assertTrue(proc.waitForFinished())

        self.assertTrue(dummy.called)
        self.assertEqual(dummy.exit_code, proc.exitCode())

    def testRelease(self):
        """PYSIDE-2646: Test whether main thread target slot lambda/methods
           (and their captured objects) are released by the signal manager
           after a while."""

        def do_connect(sender):
            receiver = Receiver()
            sender.void_signal.connect(lambda: setattr(receiver, 'called', True))
            return receiver

        sender = Sender()
        receiver = weakref.ref(do_connect(sender))
        sender.emit_void()
        self.assertTrue(receiver().called)
        del sender
        for i in range(3):
            if not receiver():
                break
            QCoreApplication.processEvents()
        self.assertFalse(receiver())


if __name__ == '__main__':
    unittest.main()
