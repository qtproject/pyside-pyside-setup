# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test for Bug 630 - Fails to resolve overload for QCursor(QBitmap, QBitmap, int, int)
http://bugs.openbossa.org/show_bug.cgi?id=630
'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtGui import QBitmap, QCursor, QPixmap
from helper.usesqapplication import UsesQApplication


class TestQCursor(UsesQApplication):
    def testQCursorConstructor(self):
        bmp = QBitmap(16, 16)
        cursor = QCursor(bmp, bmp, 16, 16)


if __name__ == '__main__':
    unittest.main()

