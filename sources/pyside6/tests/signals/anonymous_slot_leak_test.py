# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
from __future__ import annotations

'''PYSIDE-2299: Connecting anonymous callables must not leak.

"Leak" means references that survive the connection. Repeated connects do
grow the reference count while they last, because every connect creates its
own connection holding its own callable - Qt and PyQt behave the same way,
and collapsing equal callables into one connection would silently drop
invocations. What must hold is that destroying the sender releases all of it
again.
'''

import gc
import os
import sys
import unittest

from functools import partial
from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from shiboken6 import Shiboken
from PySide6.QtWidgets import QWidget
from helper.usesqapplication import UsesQApplication


have_debug = hasattr(sys, "gettotalrefcount")

CONNECTS = 1000


class TestBugPYSIDE2299(UsesQApplication):
    def leak(self, make_callable):
        # Warm-up: the first connect builds shared state that is kept.
        widget = QWidget()
        widget.windowIconChanged.connect(make_callable())
        Shiboken.delete(widget)
        del widget
        gc.collect()

        refs_before = sys.gettotalrefcount()

        widget = QWidget()
        for _ in range(CONNECTS):
            widget.windowIconChanged.connect(make_callable())
        Shiboken.delete(widget)
        del widget
        gc.collect()

        refs_after = sys.gettotalrefcount()
        self.assertAlmostEqual(refs_after - refs_before, 0, delta=10)

    @unittest.skipUnless(have_debug, "You need a debug build")
    def test_lambda(self):
        self.leak(lambda: (lambda *args: None))

    @unittest.skipUnless(have_debug, "You need a debug build")
    def test_functools_partial(self):
        self.leak(lambda: partial(int, 0))


if __name__ == '__main__':
    unittest.main()
