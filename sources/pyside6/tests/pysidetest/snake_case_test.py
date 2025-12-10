# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
from __future__ import annotations

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

from PySide6.QtWidgets import QWidget
if not is_pypy:
    from __feature__ import snake_case  # noqa
from helper.usesqapplication import UsesQApplication

import snake_case_imported
import snake_case_imported_no_snake_case


@unittest.skipIf(is_pypy, "__feature__ cannot yet be used with PyPy")
class SnakeCaseNoPropagateTest(UsesQApplication):

    def testSnakeCaseImport(self):
        """PYSIDE-3250: Test that snake case works when using it in imported modules."""
        widget = QWidget()
        r1 = widget.size_hint()
        r2 = snake_case_imported.test()
        self.assertEqual(r1, r2)

    def testSnakeCaseImportNoSnakeCase(self):
        """PYSIDE-2029: Tests that snake_case is isolated from imported modules."""
        widget = QWidget()
        r1 = widget.size_hint()
        r2 = snake_case_imported_no_snake_case.test_no_snake_case()
        self.assertEqual(r1, r2)


if __name__ == '__main__':
    unittest.main()
