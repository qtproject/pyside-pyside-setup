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
from shiboken_test_helper import objectFullname

from shiboken6 import Shiboken

from shibokensupport.signature import get_signature


class TestEnumFromRemovedNamespace(unittest.TestCase):

    @unittest.skipIf(sys.pyside63_option_python_enum, "Makes no sense with strict Enums")
    def testEnumPromotedToGlobal(self):
        sample.RemovedNamespace1_Enum
        self.assertEqual(sample.RemovedNamespace1_Enum_Value0, 0)
        self.assertEqual(sample.RemovedNamespace1_Enum_Value1, 1)
        sample.RemovedNamespace1_AnonymousEnum_Value0
        sample.RemovedNamespace2_Enum
        sample.RemovedNamespace2_Enum_Value0

    def testNames(self):
        # Test if invisible namespace does not appear on type name
        self.assertEqual(objectFullname(sample.RemovedNamespace1_Enum),
                         "sample.RemovedNamespace1_Enum")
        self.assertEqual(objectFullname(sample.ObjectOnInvisibleNamespace),
                         "sample.ObjectOnInvisibleNamespace")

        # Function arguments
        signature = get_signature(sample.ObjectOnInvisibleNamespace.toInt)
        self.assertEqual(objectFullname(signature.parameters['e'].annotation),
                         "sample.RemovedNamespace1_Enum")
        signature = get_signature(sample.ObjectOnInvisibleNamespace.consume)
        self.assertEqual(objectFullname(signature.parameters['other'].annotation),
                         "sample.ObjectOnInvisibleNamespace")

    def testGlobalFunctionFromRemovedNamespace(self):
        self.assertEqual(sample.mathSum(1, 2), 3)

    def testEnumPromotedToUpperNamespace(self):
        sample.UnremovedNamespace
        sample.UnremovedNamespace.RemovedNamespace3_Enum
        sample.UnremovedNamespace.RemovedNamespace3_Enum_Value0
        sample.UnremovedNamespace.RemovedNamespace3_AnonymousEnum_Value0

    def testNestedFunctionFromRemovedNamespace(self):
            self.assertEqual(sample.UnremovedNamespace.nestedMathSum(1, 2), 3)


if __name__ == '__main__':
    unittest.main()

