#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QCoreApplication, QParallelAnimationGroup, QSequentialAnimationGroup, QTimer


class QAnimationGroupTest(unittest.TestCase):

    def testBasic(self):
        app = QCoreApplication([])

        panim = QParallelAnimationGroup()
        sanim = QSequentialAnimationGroup()
        panim.addAnimation(sanim)

        self.assertEqual(sanim.parent(), panim)

        panim.clear()

        self.assertRaises(RuntimeError, lambda: sanim.parent())

        QTimer.singleShot(100, app.quit)
        app.exec()


if __name__ == '__main__':
    unittest.main()
