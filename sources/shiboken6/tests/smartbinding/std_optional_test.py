#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import gc
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()
from smart import Integer, StdOptionalTestBench, std


def call_func_on_optional(o):
    o.printInteger()


def integer_from_value(v):
    result = Integer()
    result.setValue(v)
    return result


class StdOptionalTests(unittest.TestCase):

    def testCInt(self):
        b = StdOptionalTestBench()
        ci = b.optionalInt()
        self.assertFalse(ci.has_value())
        b.setOptionalIntValue(42)
        ci = b.optionalInt()
        self.assertTrue(ci.has_value())
        self.assertEqual(ci.value(), 42)
        b.setOptionalInt(ci)
        ci = b.optionalInt()
        self.assertTrue(ci.has_value())
        self.assertEqual(ci.value(), 42)

        ci = std.optional_int(43)
        self.assertEqual(ci.value(), 43)

    def testInteger(self):
        b = StdOptionalTestBench()
        i = b.optionalInteger()
        self.assertFalse(i.has_value())
        self.assertFalse(i)
        # Must not throw a C++ exception
        self.assertRaises(AttributeError, call_func_on_optional, i)

        b.setOptionalIntegerValue(integer_from_value(42))
        i = b.optionalInteger()
        self.assertTrue(i.has_value())
        self.assertEqual(i.value().value(), 42)
        i.printInteger()
        print(i)
        b.setOptionalInteger(i)
        i = b.optionalInteger()
        self.assertTrue(i.has_value())
        self.assertEqual(i.value().value(), 42)
        call_func_on_optional(i)

        i = std.optional_Integer(integer_from_value(43))
        self.assertEqual(i.value().value(), 43)


if __name__ == '__main__':
    unittest.main()
