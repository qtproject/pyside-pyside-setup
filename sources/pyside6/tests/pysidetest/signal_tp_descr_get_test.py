#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

"""
PYSIDE-68: Test that signals have a `__get__` function after all.

We supply a `tp_descr_get` slot for the signal type.
That creates the `__get__` method via `PyType_Ready`.

The original test script was converted to a unittest.
See https://bugreports.qt.io/browse/PYSIDE-68 .

Created:    16 May '12 21:25
Updated:    17 Sep '20 17:02

This fix was over 8 years late. :)
"""

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject, Signal


def emit_upon_success(signal):
    def f_(f):
        def f__(self):
            result = f(self)
            s = signal.__get__(self)
            print(result)
            return result
        return f__
    return f_


class Foo(QObject):
    SIG = Signal()

    @emit_upon_success(SIG)
    def do_something(self):
        print("hooka, it worrrks")
        return 42


class UnderUnderGetUnderUnderTest(unittest.TestCase):
    def test_tp_descr_get(self):
        foo = Foo()
        ret = foo.do_something()
        self.assertEqual(ret, 42)


if __name__ == "__main__":
    unittest.main()
