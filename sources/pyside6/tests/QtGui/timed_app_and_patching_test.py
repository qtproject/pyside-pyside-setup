# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.timedqguiapplication import TimedQGuiApplication
from PySide6.support import deprecated
from PySide6.support.signature import importhandler
from PySide6 import QtGui


class TestTimedApp(TimedQGuiApplication):
    '''Simple test case for TimedQGuiApplication'''

    def testFoo(self):
        # Simple test of TimedQGuiApplication
        self.app.exec()


def fix_for_QtGui(QtGui):
    QtGui.something = 42


class TestPatchingFramework(unittest.TestCase):
    """Simple test that verifies that deprecated.py works"""

    deprecated.fix_for_QtGui = fix_for_QtGui

    def test_patch_works(self):
        something = "something"
        self.assertFalse(hasattr(QtGui, something))
        importhandler.finish_import(QtGui)
        self.assertTrue(hasattr(QtGui, something))


if __name__ == '__main__':
    unittest.main()
