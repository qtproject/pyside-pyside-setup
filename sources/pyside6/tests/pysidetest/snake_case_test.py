# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

"""
PYSIDE-2029: Tests that snake_case is isolated from imported modules
"""
is_pypy = hasattr(sys, "pypy_version_info")

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget, QSpinBox
if not is_pypy:
    from __feature__ import snake_case
from helper.usesqapplication import UsesQApplication

import snake_case_sub

@unittest.skipIf(is_pypy, "__feature__ cannot yet be used with PyPy")
class SnakeCaseNoPropagateTest(UsesQApplication):

    def testSnakeCase(self):
        # this worked
        widget = QWidget()
        check = widget.size_hint

        snake_case_sub.test_no_snake_case()


if __name__ == '__main__':
    unittest.main()
