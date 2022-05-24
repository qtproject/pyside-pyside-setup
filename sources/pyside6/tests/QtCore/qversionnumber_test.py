#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Unit tests for QVersionNumber'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QVersionNumber


class QVersionNumberTest(unittest.TestCase):
    def testFromString(self):
        versionString = '5.9.2'
        version = QVersionNumber.fromString(versionString)
        self.assertTrue(not version.isNull())
        self.assertEqual(version.majorVersion(), 5)
        self.assertEqual(version.minorVersion(), 9)
        self.assertEqual(version.microVersion(), 2)
        self.assertEqual(version.toString(), versionString)


if __name__ == '__main__':
    unittest.main()
