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


class ObjectTypeByValueTest (unittest.TestCase):
    def testIt(self):
        factory = ObjectTypeByValue()
        obj = factory.returnSomeKindOfMe()
        # This should crash!
        obj.prop.protectedValueTypeProperty.setX(1.0)
        # just to make sure it will segfault
        obj.prop.protectedValueTypeProperty.setY(2.0)

if __name__ == "__main__":
    unittest.main()
