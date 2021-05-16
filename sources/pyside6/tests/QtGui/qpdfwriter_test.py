# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.usesqapplication import UsesQApplication
from PySide6.QtGui import QPageLayout, QPageSize, QPdfWriter, QTextDocument
from PySide6.QtCore import QDir, QMarginsF, QTemporaryFile


class QPdfWriterTest(UsesQApplication):

    def testWrite(self):
        temporaryFile = QTemporaryFile(QDir.tempPath() + "/pdfwriter_test_XXXXXX.pdf")
        self.assertTrue(temporaryFile.open())
        pdfWriter = QPdfWriter(temporaryFile)
        pdfWriter.setPageLayout(QPageLayout(QPageSize(QPageSize.A4), QPageLayout.Portrait, QMarginsF(10, 10, 10, 10)))
        doc = QTextDocument("Some text")
        doc.print_(pdfWriter)
        temporaryFile.close()
        self.assertTrue(temporaryFile.size() > 0)


if __name__ == '__main__':
    unittest.main()
