# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for QResource usage'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QByteArray, QFile, QIODevice
import resources_mc


class ResourcesUsage(unittest.TestCase):
    '''Test case for resources usage'''

    def testPhrase(self):
        # Test loading of quote.txt resource
        file = Path(__file__).resolve().parent / 'quoteEnUS.txt'
        self.assertTrue(file.is_file())
        orig = QByteArray(file.read_bytes())
        # In case the file is checked out in 'crlf' mode, strip '\r'
        # since we read binary.
        if sys.platform == 'win32':
            carriage_return = orig.indexOf('\r')
            if carriage_return != -1:
                orig.remove(carriage_return, 1)

        f = QFile(':/quote.txt')  #|QIODevice.Text
        self.assertTrue(f.open(QIODevice.ReadOnly), f.errorString())
        copy = f.readAll()
        f.close()
        self.assertEqual(orig, copy)

    def testImage(self):
        # Test loading of sample.png resource
        file = Path(__file__).resolve().parent / 'sample.png'
        self.assertTrue(file.is_file())
        orig = file.read_bytes()

        f = QFile(':/sample.png')
        self.assertTrue(f.open(QIODevice.ReadOnly), f.errorString())
        copy = f.readAll()
        f.close()
        self.assertEqual(len(orig), len(copy))
        self.assertEqual(orig, copy)


if __name__ == '__main__':
    unittest.main()

