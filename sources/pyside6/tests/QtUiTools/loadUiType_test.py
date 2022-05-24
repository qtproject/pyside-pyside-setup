# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.usesqapplication import UsesQApplication

from PySide6.QtWidgets import QWidget, QFrame, QPushButton
from PySide6.QtUiTools import loadUiType


class loadUiTypeTester(UsesQApplication):
    def testFunction(self):
        filePath = os.path.join(os.path.dirname(__file__), "minimal.ui")
        loaded = loadUiType(filePath)
        self.assertNotEqual(loaded, None)

        # (<class '__main__.Ui_Form'>, <class 'PySide6.QtWidgets.QFrame'>)
        generated, base = loaded

        # Generated class contains retranslateUi method
        self.assertTrue("retranslateUi" in dir(generated))

        # Base class instance will be QFrame for this example
        self.assertTrue(isinstance(base(), QFrame))

        anotherFileName = os.path.join(os.path.dirname(__file__), "test.ui")
        another = loadUiType(anotherFileName)
        self.assertNotEqual(another, None)

        generated, base = another
        # Base class instance will be QWidget for this example
        self.assertTrue(isinstance(base(), QWidget))

        w = base()
        ui = generated()
        ui.setupUi(w)

        self.assertTrue(isinstance(ui.child_object, QFrame))
        self.assertTrue(isinstance(ui.grandson_object, QPushButton))


if __name__ == '__main__':
    unittest.main()

