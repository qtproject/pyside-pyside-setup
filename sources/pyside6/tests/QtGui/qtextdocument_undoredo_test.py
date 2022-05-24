# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtGui import QTextDocument, QTextCursor


class QTextDocumentTest(unittest.TestCase):

    def testUndoRedo(self):
        text = 'foobar'
        doc = QTextDocument(text)

        self.assertFalse(doc.isRedoAvailable())
        self.assertTrue(doc.isUndoAvailable())
        self.assertEqual(doc.toPlainText(), text)

        cursor = QTextCursor(doc)
        doc.undo(cursor)

        self.assertTrue(doc.isRedoAvailable())
        self.assertFalse(doc.isUndoAvailable())
        self.assertEqual(doc.toPlainText(), '')

        doc.redo(cursor)

        self.assertFalse(doc.isRedoAvailable())
        self.assertTrue(doc.isUndoAvailable())
        self.assertEqual(doc.toPlainText(), text)


if __name__ == '__main__':
    unittest.main()

