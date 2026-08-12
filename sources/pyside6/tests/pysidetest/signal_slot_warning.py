#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
from __future__ import annotations

''' PYSIDE-315: Test that adding a signal after class creation is rejected.

Signals are named and registered while the type is parsed. A Signal assigned
to the class afterwards never reaches the meta object: it used to bind to an
instance with the signature "()", which Qt connects by index without checking
arguments, so emitting it read arguments that were never written. Binding such
a signal must fail instead.
'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths  # noqa: E402
init_test_paths(False)

import PySide6.QtCore as QtCore  # noqa: E402


class Whatever(QtCore.QObject):
    echoSignal = QtCore.Signal(str)

    def __init__(self):
        super().__init__()
        self.echoSignal.connect(self.mySlot)

    def mySlot(self, v):
        pass


class LateSignalTest(unittest.TestCase):
    def testLateSignalRejected(self):
        obj = Whatever()
        # Insert a signal after the type has been parsed.
        setattr(Whatever, "foo", QtCore.Signal())
        with self.assertRaises(RuntimeError) as cm:
            obj.foo
        self.assertIn("added after the class was created", str(cm.exception))

    def testDeclaredSignalStillWorks(self):
        obj = Whatever()
        received = []
        obj.echoSignal.connect(received.append)
        obj.echoSignal.emit("hello")
        self.assertEqual(received, ["hello"])


if __name__ == "__main__":
    unittest.main()
