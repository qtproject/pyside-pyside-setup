# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
from __future__ import annotations

'''Test cases for QBrush'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush, QConicalGradient

from helper.usesqapplication import UsesQApplication


class Constructor(UsesQApplication):
    '''Test case for constructor of QBrush'''

    def testQColor(self):
        # QBrush(QColor) constructor
        color = QColor('black')
        obj = QBrush(color)
        self.assertEqual(obj.color(), color)

        obj = QBrush(Qt.blue)
        self.assertEqual(obj.color(), Qt.blue)

    def testGradient(self):
        """Test type discovery on class hierarchies with non-virtual
           destructors by specifying a polymorphic-id-expression without
           polymorphic-name-function."""
        gradient = QConicalGradient()
        brush = QBrush(gradient)
        self.assertEqual(type(brush.gradient()), type(gradient))


if __name__ == '__main__':
    unittest.main()
