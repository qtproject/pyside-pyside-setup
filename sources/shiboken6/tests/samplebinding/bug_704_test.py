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

from sample import ObjectType


class NewStyle(object):
    def name(self):
        return "NewStyle"


def defineNewStyle():
    class MyObjectNew(ObjectType, NewStyle):
        pass


class ObjectTypeTest(unittest.TestCase):
    '''Test cases to avoid declaring Shiboken classes with multiple inheritance from old style classes.'''

    def testObjectTypeNewStype(self):
        defineNewStyle()



if __name__ == '__main__':
    unittest.main()

