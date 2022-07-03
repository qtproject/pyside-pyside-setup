#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for functions signature'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from other import OtherObjectType
from shiboken_test_helper import objectFullname

from shiboken6 import Shiboken

from shibokensupport.signature import get_signature


class SignatureTest(unittest.TestCase):

    # Check if the argument of
    # 'OtherObjectType::enumAsInt(SampleNamespace::SomeClass::PublicScopedEnum value)'
    # has the correct representation
    def testNamespaceFromOtherModule(self):
        argType = get_signature(OtherObjectType.enumAsInt).parameters["value"].annotation
        self.assertEqual(objectFullname(argType),
            "sample.SampleNamespace.SomeClass.PublicScopedEnum")


if __name__ == '__main__':
    unittest.main()
