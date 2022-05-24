# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QSizeF, QTimer
from PySide6.QtGui import QTextFormat, QTextCharFormat, QPyTextObject
from PySide6.QtWidgets import QTextEdit
from helper.usesqapplication import UsesQApplication


class Foo(QPyTextObject):
    called = False

    def intrinsicSize(self, doc, posInDocument, format):
        Foo.called = True
        return QSizeF(10, 10)

    def drawObject(self, painter, rect, doc, posInDocument, format):
        pass


class QAbstractTextDocumentLayoutTest(UsesQApplication):

    objectType = QTextFormat.UserObject + 1

    def foo(self):
        fmt = QTextCharFormat()
        fmt.setObjectType(QAbstractTextDocumentLayoutTest.objectType)

        cursor = self.textEdit.textCursor()
        cursor.insertText(chr(0xfffc), fmt)
        self.textEdit.setTextCursor(cursor)
        self.textEdit.close()

    def testIt(self):

        self.textEdit = QTextEdit()
        self.textEdit.show()

        interface = Foo()
        self.textEdit.document().documentLayout().registerHandler(QAbstractTextDocumentLayoutTest.objectType, interface)

        QTimer.singleShot(0, self.foo)
        self.app.exec()

        self.assertTrue(Foo.called)


if __name__ == "__main__":
    unittest.main()

