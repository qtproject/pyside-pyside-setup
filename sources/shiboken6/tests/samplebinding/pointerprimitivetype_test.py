#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

"""
pointerprimitivetype_test.py

check that the primitive types are correctly mapped by the signature module.

Mapping
-------
IntArray2(const int*)                 --  <Signature (self, data: typing.Sequence)>
getMargins(int*,int*,int*,int*)const  --  <Signature (self) -> typing.Tuple[int, int, int, int]>

We explicitly check only against typing.Iterable in the first test,
because typing.Sequence is a subclass, but we will generalize this
to typing.Iterable in the future.
"""

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()
from sample import IntArray2, VirtualMethods

import shiboken6
from shibokensupport.signature import get_signature

import typing


class PointerPrimitiveTypeTest(unittest.TestCase):

    def testArraySignature(self):
        # signature="IntArray2(const int*)"
        found = False
        for sig in get_signature(IntArray2):
            if "data" in sig.parameters:
                found = True
                break
        self.assertTrue(found)
        ann = sig.parameters["data"].annotation
        self.assertEqual(ann.__args__, (int,))
        self.assertTrue(issubclass(ann.__origin__, typing.Iterable))

    def testReturnVarSignature(self):
        # signature="getMargins(int*,int*,int*,int*)const">
        ann = get_signature(VirtualMethods.getMargins).return_annotation
        self.assertEqual(ann, typing.Tuple[int, int, int, int])


if __name__ == '__main__':
    unittest.main()
