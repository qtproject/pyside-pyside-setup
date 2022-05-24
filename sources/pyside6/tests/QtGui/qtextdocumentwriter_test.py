# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtGui import QTextDocumentWriter, QTextDocument
from PySide6.QtCore import QBuffer


class QTextDocumentWriterTest(unittest.TestCase):

    def testWrite(self):
        text = 'foobar'
        doc = QTextDocument(text)
        b = QBuffer()
        b.open(QBuffer.ReadWrite)
        writer = QTextDocumentWriter(b, bytes("plaintext", "UTF-8"))
        writer.write(doc)
        b.close()
        self.assertEqual(b.buffer(), text)


if __name__ == '__main__':
    unittest.main()
