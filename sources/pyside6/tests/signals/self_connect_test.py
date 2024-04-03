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

from PySide6.QtCore import QObject, Slot
from PySide6.QtWidgets import QPushButton, QWidget

from helper.usesqapplication import UsesQApplication


class Receiver(QObject):
    def __init__(self, p=None):
        super().__init__(p)
        self.triggered = False

    @Slot(bool, int)
    def default_parameter_slot(self, bool_value, int_value=0):
        self.triggered = True


class SelfConnect(UsesQApplication):

    def testButtonClickClose(self):
        button = QPushButton()
        button.clicked.connect(button.close)

        button.show()
        self.assertTrue(button.isVisible())
        button.click()
        self.assertTrue(not button.isVisible())

    def testWindowButtonClickClose(self):
        button = QPushButton()
        window = QWidget()
        button.clicked.connect(window.close)

        window.show()
        self.assertTrue(window.isVisible())
        button.click()
        self.assertTrue(not window.isVisible())

    def testDefaultParameters(self):
        button = QPushButton()
        receiver = Receiver(button)
        button.clicked.connect(receiver.default_parameter_slot)
        button.clicked.connect(button.close)
        button.show()
        button.click()
        self.assertTrue(receiver.triggered)


if __name__ == '__main__':
    unittest.main()
