#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest
import warnings

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import ObjectType

class TestDeprecatedCall(unittest.TestCase):
    def testCallWithError(self):
        o = ObjectType()
        warnings.simplefilter('error')
        self.assertRaises(DeprecationWarning, o.deprecatedFunction)

if __name__ == '__main__':
    unittest.main()
