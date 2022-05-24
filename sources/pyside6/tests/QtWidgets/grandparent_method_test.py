# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Tests for calling methods further than the direct parent'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtWidgets import QPushButton, QWidget

from helper.usesqapplication import UsesQApplication


class Dummy(QPushButton):

    def show(self):
        QWidget.show(self)
        self.called = True


class GrandParentMethod(UsesQApplication):
    def testMethod(self):
        obj = Dummy()
        obj.show()
        self.assertTrue(obj.called)


if __name__ == '__main__':
    unittest.main()
