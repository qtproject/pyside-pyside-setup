#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for QCoreApplication.instance static method'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QCoreApplication


class QCoreApplicationInstanceTest(unittest.TestCase):
    '''Test cases for QCoreApplication.instance static method'''

    def testQCoreApplicationInstance(self):
        # Tests QCoreApplication.instance()
        self.assertEqual(QCoreApplication.instance(), None)
        app = QCoreApplication([])
        self.assertEqual(QCoreApplication.instance(), app)


if __name__ == '__main__':
    unittest.main()

