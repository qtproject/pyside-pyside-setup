# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import sys

try:
    import sysconfig
    if bool(sysconfig.get_config_var('Py_DEBUG')):
        sys.exit(0)
    import numpy
except:
    sys.exit(0)

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()
from sample import PointF

class TestNumpyTypes(unittest.TestCase):

    def testNumpyConverted(self):
        x, y = (0.1, 0.2)
        p = PointF(float(numpy.float32(x)), float(numpy.float32(y)))
        self.assertAlmostEqual(p.x(), x)
        self.assertAlmostEqual(p.y(), y)

    def testNumpyAsIs(self):
        x, y = (0.1, 0.2)
        p = PointF(numpy.float32(x), numpy.float32(y))
        self.assertAlmostEqual(p.x(), x)
        self.assertAlmostEqual(p.y(), y)

if __name__ == "__main__":
    unittest.main()

