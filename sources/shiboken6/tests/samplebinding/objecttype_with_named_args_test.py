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

class NamedArgsTest(unittest.TestCase):

    def testOneArgument(self):
        p = ObjectType()
        o = ObjectType(parent=p)
        self.assertEqual(o.parent(), p)

    def testMoreArguments(self):
        o = ObjectType()

        o.setObjectSplittedName("", prefix="pys", suffix="ide")
        self.assertEqual(o.objectName(), "pyside")

        o.setObjectSplittedName("", suffix="ide", prefix="pys")
        self.assertEqual(o.objectName(), "pyside")

        o.setObjectNameWithSize(name="pyside", size=6)
        self.assertEqual(o.objectName(), "pyside")

        o.setObjectNameWithSize(size=6, name="pyside")
        self.assertEqual(o.objectName(), "pyside")


    def testUseDefaultValues(self):
        o = ObjectType()

        o.setObjectNameWithSize(size=3)
        self.assertEqual(o.objectName(), "<un") # use name='unknown' default argument

        o.setObjectSplittedName("")
        self.assertEqual(o.objectName(), "<unknown>") # user prefix='<unk' and suffix='nown>'



if __name__ == '__main__':
    unittest.main()

