# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''(Very) Simple test case for missing names from QtCore'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6 import QtCore


class MissingClasses(unittest.TestCase):

    def testQSettings(self):  # Bug 232
        getattr(QtCore, 'QSettings')

    def testQtTrNoop(self):  # Bug 220
        getattr(QtCore, 'QT_TR_NOOP')


if __name__ == '__main__':
    unittest.main()
