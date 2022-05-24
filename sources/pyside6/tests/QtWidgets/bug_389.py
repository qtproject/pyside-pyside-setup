# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

''' Test bug 389: http://bugs.openbossa.org/show_bug.cgi?id=389'''

import sys
import os
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.usesqapplication import UsesQApplication
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QStyle, QWidget


class BugTest(UsesQApplication):
    def testCase(self):
        s = QWidget().style()
        i = s.standardIcon(QStyle.SP_TitleBarMinButton)
        self.assertEqual(type(i), QIcon)


if __name__ == '__main__':
    unittest.main()
