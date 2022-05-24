#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for QLockFile'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
sys.path.append(os.fspath(Path(__file__).resolve().parents[1] / "util"))
from init_paths import init_test_paths
init_test_paths()

from PySide6.QtCore import QDir, QLockFile, QCoreApplication


class TestQMessageAuthenticationCode (unittest.TestCase):

    def setUp(self):
        pid = QCoreApplication.applicationPid()
        self._fileName = f"{QDir.tempPath()}/pqlockfiletest{pid}.tmp"

    def tearDown(self):
        if (os.path.exists(self._fileName)):
            os.remove(self._fileName)

    def test(self):
        # Merely exercise the API, no locking against another processes.
        lockFile = QLockFile(self._fileName)
        self.assertTrue(lockFile.lock())
        self.assertTrue(lockFile.isLocked())
        lockFile.unlock()


if __name__ == '__main__':
    unittest.main()
