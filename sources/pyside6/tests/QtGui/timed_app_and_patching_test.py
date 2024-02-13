# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths  # noqa: E402
init_test_paths(False)

from helper.timedqguiapplication import TimedQGuiApplication


class TestTimedApp(TimedQGuiApplication):
    '''Simple test case for TimedQGuiApplication'''

    def testFoo(self):
        # Simple test of TimedQGuiApplication
        self.app.exec()

# deprecated.py is no longer needed.


if __name__ == '__main__':
    unittest.main()
