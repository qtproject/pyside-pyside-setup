# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

import PySide6

# Note:
# "from PySide6 import *" can only be used at module level.
# It is also really not recommended to use. But for testing,
# the "__all__" variable is a great feature!


class AllModulesImportTest(unittest.TestCase):
    def testAllModulesCanImport(self):
        # would also work: exec("from PySide6 import *")
        for name in PySide6.__all__:
            exec(f"import PySide6.{name}")


if __name__ == '__main__':
    unittest.main()
