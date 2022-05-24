# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject, SIGNAL, Qt


class Dummy(QObject):
    """Dummy class used in this test."""
    def __init__(self, parent=None):
        QObject.__init__(self, parent)


class TestConnectionTypeSupport(unittest.TestCase):
    def callback(self, *args):
        if tuple(self.args) == args:
            self.called = True

    def testNoArgs(self):
        """Connect signal using a Qt.ConnectionType as argument"""
        obj1 = Dummy()

        QObject.connect(obj1, SIGNAL('foo()'), self.callback, Qt.DirectConnection)
        self.args = tuple()
        obj1.emit(SIGNAL('foo()'), *self.args)

        self.assertTrue(self.called)


if __name__ == '__main__':
    unittest.main()
