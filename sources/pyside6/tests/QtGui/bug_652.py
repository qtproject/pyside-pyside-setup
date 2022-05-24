# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import gc
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtGui import QTextBlockUserData, QTextCursor, QTextDocument


class MyData(QTextBlockUserData):
    def __init__(self, data):
        super().__init__()
        self.data = data

    def getMyNiceData(self):
        return self.data


class TestBug652(unittest.TestCase):
    """Segfault when using QTextBlock::setUserData due to missing ownership transfer"""
    def testIt(self):
        td = QTextDocument()
        tc = QTextCursor(td)
        tc.insertText("Hello world")
        heyHo = "hey ho!"
        tc.block().setUserData(MyData(heyHo))
        self.assertEqual(type(tc.block().userData()), MyData)
        self.assertEqual(tc.block().userData().getMyNiceData(), heyHo)

        del tc
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        tc = QTextCursor(td)
        blk = tc.block()
        self.assertEqual(type(blk.userData()), MyData)
        self.assertEqual(blk.userData().getMyNiceData(), heyHo)


if __name__ == "__main__":
    unittest.main()
