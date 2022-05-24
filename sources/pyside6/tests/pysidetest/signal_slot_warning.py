#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

''' PYSIDE-315: https://bugreports.qt.io/browse/PYSIDE-315
    Test that creating a signal in the wrong order triggers a warning. '''

import os
import sys
import unittest
import warnings

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

import PySide6.QtCore as QtCore


class Whatever(QtCore.QObject):
    echoSignal = QtCore.Signal(str)

    def __init__(self):
        super().__init__()
        self.echoSignal.connect(self.mySlot)

    def mySlot(self, v):
        pass


class WarningTest(unittest.TestCase):
    def testSignalSlotWarning(self):
        # we create an object. This gives no warning.
        obj = Whatever()
        # then we insert a signal after slots have been created.
        setattr(Whatever, "foo", QtCore.Signal())
        with warnings.catch_warnings(record=True) as w:
            # Cause all warnings to always be triggered.
            warnings.simplefilter("always")
            # Trigger a warning.
            obj.foo.connect(obj.mySlot)
            # Verify some things
            assert issubclass(w[-1].category, RuntimeWarning)
            assert "*** Sort Warning ***" in str(w[-1].message)
            # note that this warning cannot be turned into an error (too hard)


if __name__ == "__main__":
    unittest.main()
