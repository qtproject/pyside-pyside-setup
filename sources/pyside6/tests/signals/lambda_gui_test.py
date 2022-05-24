# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Connecting lambda to gui signals'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject, SIGNAL

try:
    from PySide6.QtWidgets import QSpinBox, QPushButton
    hasQtGui = True
except ImportError:
    hasQtGui = False

from helper.usesqapplication import UsesQApplication

if hasQtGui:
    class Control:
        def __init__(self):
            self.arg = False

    class QtGuiSigLambda(UsesQApplication):

        def testButton(self):
            # Connecting a lambda to a QPushButton.clicked()
            obj = QPushButton('label')
            ctr = Control()
            func = lambda: setattr(ctr, 'arg', True)
            obj.clicked.connect(func)
            obj.click()
            self.assertTrue(ctr.arg)
            QObject.disconnect(obj, SIGNAL('clicked()'), func)

        def testSpinButton(self):
            # Connecting a lambda to a QPushButton.clicked()
            obj = QSpinBox()
            ctr = Control()
            arg = 444
            func = lambda x: setattr(ctr, 'arg', 444)
            obj.valueChanged.connect(func)
            obj.setValue(444)
            self.assertEqual(ctr.arg, arg)
            QObject.disconnect(obj, SIGNAL('valueChanged(int)'), func)

if __name__ == '__main__':
    unittest.main()
