# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()
from sample import *
from other import *
from shiboken6 import Shiboken

class TestHashFuncs (unittest.TestCase):

    def testIt(self):
        obj1 = HandleHolder()
        obj2 = HandleHolder()

        hash1 = hash(obj1)
        hash2 = hash(obj2)
        self.assertNotEqual(hash1, hash2)

        # Now invalidate the object and test its hash.  It shouldn't segfault.
        Shiboken.invalidate(obj1)

        hash1_2 = hash(obj1)
        self.assertEqual(hash1_2, hash1)



if __name__ == '__main__':
    unittest.main()
