#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Using self.connect(signal, method)'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject, SIGNAL, SLOT
from PySide6.QtWidgets import QPushButton, QWidget

from helper.usesqapplication import UsesQApplication


class SelfConnect(UsesQApplication):

    def testButtonClickClose(self):
        button = QPushButton()
        button.connect(button, SIGNAL('clicked()'), SLOT('close()'))

        button.show()
        self.assertTrue(button.isVisible())
        button.click()
        self.assertTrue(not button.isVisible())

    def testWindowButtonClickClose(self):
        button = QPushButton()
        window = QWidget()
        window.connect(button, SIGNAL('clicked()'), SLOT('close()'))

        window.show()
        self.assertTrue(window.isVisible())
        button.click()
        self.assertTrue(not window.isVisible())


if __name__ == '__main__':
    unittest.main()
