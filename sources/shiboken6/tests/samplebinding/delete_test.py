#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

import sample
from shiboken6 import Shiboken

class DeleteTest(unittest.TestCase):
    def testNonCppWrapperClassDelete(self):
        """Would segfault when shiboken.delete called on obj not created from
        Python """
        obj = sample.ObjectType()
        child = obj.createChild(None)
        Shiboken.delete(child)
        assert not Shiboken.isValid(child)

if __name__ == '__main__':
    unittest.main()

