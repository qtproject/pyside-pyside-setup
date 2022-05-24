# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

''' Test bug 324: http://bugs.openbossa.org/show_bug.cgi?id=324'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QCoreApplication, QObject, Signal


class QBug(QObject):
    def __init__(self, parent=None):
        QObject.__init__(self, parent)

    def check(self):
        self.done.emit("abc")

    done = Signal(str)


class Bug324(unittest.TestCase):

    def on_done(self, val):
        self.value = val

    def testBug(self):
        app = QCoreApplication([])
        bug = QBug()
        self.value = ''
        bug.done.connect(self.on_done)
        bug.check()
        self.assertEqual(self.value, 'abc')


if __name__ == '__main__':
    unittest.main()
