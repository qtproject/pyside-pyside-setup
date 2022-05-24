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

from PySide6 import __version_info__, __version__


class CheckForVariablesTest(unittest.TestCase):
    def testVesions(self):
        version_tuple = (__version_info__[0], __version_info__[1], __version_info__[2])
        self.assertTrue(version_tuple >= (1, 0, 0))

        self.assertTrue(version_tuple < (99, 99, 99))
        self.assertTrue(__version__)

        self.assertTrue(__version_info__ >= (4, 5, 0))
        self.assertTrue(__version__)


if __name__ == '__main__':
    unittest.main()

