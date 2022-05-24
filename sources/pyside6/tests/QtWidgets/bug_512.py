# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

''' Test bug 512: http://bugs.openbossa.org/show_bug.cgi?id=512'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.usesqapplication import UsesQApplication
from PySide6.QtWidgets import QGridLayout, QLabel, QWidget


class BugTest(UsesQApplication):
    def testCase(self):
        w = QWidget(None)
        lbl = QLabel("Hello", w)
        g = QGridLayout()
        g.addWidget(lbl, 0, 0)
        w.setLayout(g)
        w.show()

        t = g.getItemPosition(0)
        self.assertEqual(type(t), tuple)
        self.assertEqual(t, (0, 0, 1, 1))


if __name__ == '__main__':
    unittest.main()
