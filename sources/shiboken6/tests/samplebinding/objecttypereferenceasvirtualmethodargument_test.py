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
from sample import ObjectTypeHolder

class TestObjectTypeReferenceAsVirtualMethodArgument(unittest.TestCase):

    def testBasic(self):
        holder = ObjectTypeHolder('TheObjectFromC++')
        self.assertEqual(holder.callPassObjectTypeAsReference(), 'TheObjectFromC++')

    def testExtended(self):
        class Holder(ObjectTypeHolder):
            def passObjectTypeAsReference(self, objectType):
                return objectType.objectName().prepend(('ThisIs'))
        holder = Holder('TheObjectFromC++')
        self.assertEqual(holder.callPassObjectTypeAsReference(), 'ThisIsTheObjectFromC++')

if __name__ == '__main__':
    unittest.main()
