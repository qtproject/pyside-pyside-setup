# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Unit test for QStyleHints'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.usesqguiapplication import UsesQGuiApplication
from PySide6.QtGui import QStyleHints


class QStyleHintsTest(UsesQGuiApplication):
    def test(self):
        styleHints = self.app.styleHints()
        self.assertTrue(styleHints.startDragDistance() > 0)


if __name__ == '__main__':
    unittest.main()
