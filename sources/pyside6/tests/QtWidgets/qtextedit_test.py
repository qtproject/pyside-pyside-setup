# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for QTextEdit and ownership problems.'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtWidgets import QTextEdit

from helper.usesqapplication import UsesQApplication


class DontTouchReference(UsesQApplication):
    '''Check if the QTextTable returned by QTextCursor.insertTable() is not
    referenced by the QTextCursor that returns it.'''

    def setUp(self):
        super(DontTouchReference, self).setUp()
        self.editor = QTextEdit()
        self.cursor = self.editor.textCursor()
        self.table = self.cursor.insertTable(1, 1)

    @unittest.skipUnless(hasattr(sys, "getrefcount"), f"{sys.implementation.name} has no refcount")
    def testQTextTable(self):
        # methods which return QTextTable should not increment its reference
        self.assertEqual(sys.getrefcount(self.table), 2)
        f = self.cursor.currentFrame()
        del f
        self.assertEqual(sys.getrefcount(self.table), 2)
        # destroying the cursor should not raise any "RuntimeError: internal
        # C++ object already deleted." when accessing the QTextTable
        del self.cursor
        self.assertEqual(sys.getrefcount(self.table), 2)
        cell = self.table.cellAt(0, 0)


if __name__ == "__main__":
    unittest.main()
