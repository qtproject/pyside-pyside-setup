# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import tempfile
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QFile, QFileInfo


class QFileConstructor(unittest.TestCase):
    '''QFileInfo constructor with qfile'''

    def testBasic(self):
        '''QFileInfo(QFile)'''
        obj = QFileInfo(QFile())

    def testQFileInfoPath(self):
        # PYSIDE-1499: Test QFileInfo with Path objects
        test_path = Path("some") / "dir"
        qinf1 = QFileInfo(os.fspath(test_path))
        qinf2 = QFileInfo(test_path)
        self.assertEqual(qinf1, qinf2)


if __name__ == '__main__':
    unittest.main()
