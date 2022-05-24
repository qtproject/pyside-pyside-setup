#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QMutex


class Lock(QMutex):
    def tryLock(self, timeout=10):
        return QMutex.tryLock(self, timeout)


class TestBug(unittest.TestCase):

    def testCase(self):
        l = Lock()
        l.tryLock()  # this cause a assertion


if __name__ == '__main__':
    unittest.main()
