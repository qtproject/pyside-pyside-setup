# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for Virtual functions with wrong return type'''

import os
import sys
import unittest
import warnings

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtWidgets import QWidget
from helper.usesqapplication import UsesQApplication


warnings.simplefilter('error')


class MyWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def sizeHint(self):
        pass


class testCase(UsesQApplication):

    def testVirtualReturn(self):
        w = MyWidget()
        self.assertWarns(RuntimeWarning, w.show)


if __name__ == '__main__':
    unittest.main()
