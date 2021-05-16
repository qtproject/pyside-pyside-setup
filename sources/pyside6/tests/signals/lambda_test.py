#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Connecting lambda to signals'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject, SIGNAL, QProcess

from helper.usesqapplication import UsesQApplication


class Dummy(QObject):

    def __init__(self, *args):
        super().__init__(*args)


class BasicCase(unittest.TestCase):

    def testSimplePythonSignalNoArgs(self):
        # Connecting a lambda to a simple python signal without arguments
        obj = Dummy()
        QObject.connect(obj, SIGNAL('foo()'),
                        lambda: setattr(obj, 'called', True))
        obj.emit(SIGNAL('foo()'))
        self.assertTrue(obj.called)

    def testSimplePythonSignal(self):
        # Connecting a lambda to a simple python signal witharguments
        obj = Dummy()
        arg = 42
        QObject.connect(obj, SIGNAL('foo(int)'),
                        lambda x: setattr(obj, 'arg', 42))
        obj.emit(SIGNAL('foo(int)'), arg)
        self.assertEqual(obj.arg, arg)


class QtSigLambda(UsesQApplication):

    qapplication = True

    def testNoArgs(self):
        '''Connecting a lambda to a signal without arguments'''
        proc = QProcess()
        dummy = Dummy()
        QObject.connect(proc, SIGNAL('started()'),
                        lambda: setattr(dummy, 'called', True))
        proc.start(sys.executable, ['-c', '""'])
        proc.waitForFinished()
        self.assertTrue(dummy.called)

    def testWithArgs(self):
        '''Connecting a lambda to a signal with arguments'''
        proc = QProcess()
        dummy = Dummy()
        QObject.connect(proc, SIGNAL('finished(int)'),
                        lambda x: setattr(dummy, 'called', x))
        proc.start(sys.executable, ['-c', '""'])
        proc.waitForFinished()
        self.assertEqual(dummy.called, proc.exitCode())


if __name__ == '__main__':
    unittest.main()
