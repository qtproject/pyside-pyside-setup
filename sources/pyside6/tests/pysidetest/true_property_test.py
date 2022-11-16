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
PYSIDE-2042: Tests true_property with inheritance
"""

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget, QSpinBox
from __feature__ import true_property
from helper.usesqapplication import UsesQApplication


class TruePropertyInheritanceTest(UsesQApplication):

    def testTrueProperty(self):
        # this worked
        widget = QWidget()
        check = widget.sizeHint
        self.assertEqual(type(check), QSize)

        # PYSIDE-2042: inheritance did not work
        spin_box = QSpinBox()
        check = spin_box.sizeHint
        self.assertEqual(type(check), QSize)


if __name__ == '__main__':
    unittest.main()
