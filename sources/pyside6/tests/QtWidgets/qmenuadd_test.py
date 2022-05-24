# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

''' Test the QMenu.addAction() method'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtWidgets import QMenu
from helper.usesqapplication import UsesQApplication


class QMenuAddAction(UsesQApplication):

    def openFile(self, *args):
        self.arg = args

    def testQMenuAddAction(self):
        fileMenu = QMenu("&File")

        addNewAction = fileMenu.addAction("&Open...", self.openFile)
        addNewAction.trigger()
        self.assertEqual(self.arg, ())


if __name__ == '__main__':
    unittest.main()
