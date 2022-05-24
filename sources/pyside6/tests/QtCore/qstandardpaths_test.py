#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Unit tests for QStandardPaths'''

import ctypes
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QStandardPaths


class QStandardPathsTest(unittest.TestCase):
    def testTestModeEnabled(self):
        print("QStandardPaths.isTestModeEnabled:", QStandardPaths.isTestModeEnabled())
        sp = True
        QStandardPaths.setTestModeEnabled(sp)
        self.assertEqual(QStandardPaths.isTestModeEnabled(), sp)
        sp = False
        QStandardPaths.setTestModeEnabled(sp)
        self.assertEqual(QStandardPaths.isTestModeEnabled(), sp)


if __name__ == '__main__':
    unittest.main()
