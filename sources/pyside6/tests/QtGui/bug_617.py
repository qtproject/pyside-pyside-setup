# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QEvent
from PySide6.QtGui import QColor


class MyEvent(QEvent):
    def __init__(self):
        QEvent.__init__(self, QEvent.Type(999))


class Bug617(unittest.TestCase):
    def testRepr(self):
        c = QColor.fromRgb(1, 2, 3, 4)
        s = c.spec()
        self.assertEqual(repr(s), repr(QColor.Rgb))

    def testOutOfBounds(self):
        e = MyEvent()
        self.assertEqual(repr(e.type()), "<Type.999: 999>"
            if sys.pyside63_option_python_enum else "PySide6.QtCore.QEvent.Type(999)")


if __name__ == "__main__":
    unittest.main()
