# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence

from helper.usesqguiapplication import UsesQGuiApplication


class QKeySequenceTest(UsesQGuiApplication):

    def testGetItemOperator(self):
        # bug #774
        ks = QKeySequence(Qt.SHIFT, Qt.CTRL, Qt.Key_P, Qt.Key_R)
        self.assertEqual(ks[0], Qt.SHIFT)
        self.assertEqual(ks[1], Qt.CTRL)
        self.assertEqual(ks[2], Qt.Key_P)
        self.assertEqual(ks[3], Qt.Key_R)


if __name__ == '__main__':
    unittest.main()
