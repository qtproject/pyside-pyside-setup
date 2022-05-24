# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest
import weakref

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.usesqapplication import UsesQApplication

from PySide6.QtGui import QTextBlockUserData, QTextCursor
from PySide6.QtWidgets import QTextEdit


class TestUserData(QTextBlockUserData):
    def __init__(self, data):
        super().__init__()
        self.data = data


class TestUserDataRefCount(UsesQApplication):
    @unittest.skipUnless(hasattr(sys, "getrefcount"), f"{sys.implementation.name} has no refcount")
    def testRefcount(self):
        textedit = QTextEdit()
        textedit.setReadOnly(True)
        doc = textedit.document()
        cursor = QTextCursor(doc)
        cursor.insertText("PySide Rocks")
        ud = TestUserData({"Life": 42})
        self.assertEqual(sys.getrefcount(ud), 2)
        cursor.block().setUserData(ud)
        self.assertEqual(sys.getrefcount(ud), 3)
        ud2 = cursor.block().userData()
        self.assertEqual(sys.getrefcount(ud), 4)
        self.udata = weakref.ref(ud, None)
        del ud, ud2
        self.assertEqual(sys.getrefcount(self.udata()), 2)


if __name__ == '__main__':
    unittest.main()
