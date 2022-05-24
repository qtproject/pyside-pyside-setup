# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QStyle

from helper.usesqapplication import UsesQApplication


class StandardPixmapTest(UsesQApplication):
    def testDefaultOptions(self):  # Bug 253
        pixmap = self.app.style().standardPixmap(QStyle.SP_DirClosedIcon)
        self.assertTrue(isinstance(pixmap, QPixmap))


if __name__ == '__main__':
    unittest.main()

