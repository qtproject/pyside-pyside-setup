# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject, Signal, Qt


class Sender(QObject):
    """Dummy class used in this test."""

    foo = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)


class TestConnectionTypeSupport(unittest.TestCase):
    def callback(self, *args):
        if tuple(self.args) == args:
            self.called = True

    def testNoArgs(self):
        """Connect signal using a Qt.ConnectionType as argument"""
        obj1 = Sender()

        obj1.foo.connect(self.callback, Qt.DirectConnection)
        self.args = tuple()
        obj1.foo.emit(*self.args)

        self.assertTrue(self.called)


if __name__ == '__main__':
    unittest.main()
