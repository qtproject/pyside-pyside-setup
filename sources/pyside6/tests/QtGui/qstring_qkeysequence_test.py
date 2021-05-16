#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Tests conversions of QString to and from QKeySequence.'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.usesqapplication import UsesQApplication

from PySide6.QtGui import QAction, QKeySequence


class QStringQKeySequenceTest(UsesQApplication):
    '''Tests conversions of QString to and from QKeySequence.'''

    def testQStringFromQKeySequence(self):
        '''Creates a QString from a QKeySequence.'''
        keyseq = 'Ctrl+A'
        a = QKeySequence(keyseq)
        self.assertEqual(a, keyseq)

    def testPythonStringAsQKeySequence(self):
        '''Passes a Python string to an argument expecting a QKeySequence.'''
        keyseq = 'Ctrl+A'
        action = QAction(None)
        action.setShortcut(keyseq)
        shortcut = action.shortcut()
        self.assertTrue(isinstance(shortcut, QKeySequence))
        self.assertEqual(shortcut.toString(), keyseq)


if __name__ == '__main__':
    unittest.main()

