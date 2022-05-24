# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QIODevice, QTemporaryFile


class FileChild1(QTemporaryFile):
    pass


class FileChild2(QTemporaryFile):
    def readData(self, maxlen):
        return super(FileChild2, self).readData(maxlen)

    def readLineData(self, maxlen):
        return super(FileChild2, self).readLineData(maxlen)


class readDataTest(unittest.TestCase):
    '''Test case for readData and readLineData'''

    def setUp(self):
        '''Acquire resources'''
        self.filename1 = FileChild1()
        self.assertTrue(self.filename1.open())
        self.filename1.write(bytes('Test text for testing', "UTF-8"))

        self.filename2 = FileChild2()
        self.assertTrue(self.filename2.open())
        self.filename2.write(bytes('Test text for testing', "UTF-8"))

    def tearDown(self):
        '''release resources'''
        pass

    def testBasic(self):
        '''QTemporaryFile.read'''
        self.filename1.seek(0)
        s1 = self.filename1.read(50)
        self.assertEqual(s1, 'Test text for testing')

    def testBug40(self):
        self.filename2.seek(0)
        s2 = self.filename2.read(50)
        self.assertEqual(s2, 'Test text for testing')

        self.filename2.seek(0)
        s2 = self.filename2.readLine(22)
        self.assertEqual(s2, 'Test text for testing')

        self.filename1.seek(0)
        s1 = self.filename1.read(50)
        self.assertEqual(s1, s2)


if __name__ == '__main__':
    unittest.main()
