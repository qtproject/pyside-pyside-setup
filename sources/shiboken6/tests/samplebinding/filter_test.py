# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import Data, Intersection, Union

class TestFilters(unittest.TestCase):

    def testAnd(self):

        f1 = Data(Data.Name, "joe")
        f2 = Union()

        inter = f1 & f2

        self.assertEqual(type(inter), Intersection)

if __name__ == '__main__':
    unittest.main()
