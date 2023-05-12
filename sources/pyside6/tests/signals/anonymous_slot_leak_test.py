# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from functools import partial
from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtWidgets import QWidget
from helper.usesqapplication import UsesQApplication


have_debug = hasattr(sys, "gettotalrefcount")


class LeakerLambda():
    def __init__(self, widget):
        widget.windowIconChanged.connect(lambda *args: None)


class LeakerFunctoolsPartial():
    def __init__(self, widget):
        widget.windowIconChanged.connect(partial(int, 0))


class TestBugPYSIDE2299(UsesQApplication):
    def leak(self, leaker):
        widget = QWidget()

        # Warm-up
        leaker(widget)

        refs_before = sys.gettotalrefcount()
        for _ in range(1000):
            leaker(widget)
        refs_after = sys.gettotalrefcount()

        self.assertAlmostEqual(refs_after - refs_before, 0, delta=10)

    @unittest.skipUnless(have_debug, "You need a debug build")
    def test_lambda(self):
        self.leak(LeakerLambda)

    @unittest.skipUnless(have_debug, "You need a debug build")
    def test_functools_partial(self):
        self.leak(LeakerFunctoolsPartial)


if __name__ == '__main__':
    unittest.main()
