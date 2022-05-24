#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test suite for QtCore.Qt namespace'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import Qt


class QtNamespace(unittest.TestCase):
    '''Test case for accessing attributes from Qt namespace'''

    def testBasic(self):
        # Access to Qt namespace
        getattr(Qt, 'Horizontal')
        getattr(Qt, 'WindowMaximizeButtonHint')
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
