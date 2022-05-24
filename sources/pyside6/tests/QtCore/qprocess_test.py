#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for QProcess'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QProcess


class TestQProcess (unittest.TestCase):
    def testStartDetached(self):
        value, pid = QProcess.startDetached("dir", [], os.getcwd())
        self.assertTrue(isinstance(value, bool))
        self.assertTrue(isinstance(pid, int))

    def testPid(self):
        p = QProcess()
        p.start("dir", [])
        p.waitForStarted()
        pid = p.processId()
        # We can't test the pid method result because it returns 0 when the
        # process isn't running
        if p.state() == QProcess.Running:
            self.assertNotEqual(pid, 0)
            p.waitForFinished()
        else:
            print("PROCESS ALREADY DEAD :-/")


if __name__ == '__main__':
    unittest.main()
