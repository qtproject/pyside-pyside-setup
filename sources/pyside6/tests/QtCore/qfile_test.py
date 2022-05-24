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

from PySide6.QtCore import QDir, QFile, QIODevice, QSaveFile, QTemporaryDir


class GetCharTest(unittest.TestCase):
    '''Test case for QIODevice.getChar in QFile'''

    def setUp(self):
        '''Acquire resources'''
        handle, self.filename = tempfile.mkstemp()
        os.write(handle, bytes('a', "UTF-8"))
        os.close(handle)

    def tearDown(self):
        '''release resources'''
        os.remove(self.filename)

    def testBasic(self):
        '''QFile.getChar'''
        obj = QFile(self.filename)
        obj.open(QIODevice.ReadOnly)
        try:
            self.assertEqual(obj.getChar(), (True, 'a'))
            self.assertFalse(obj.getChar()[0])
        finally:
            obj.close()

    def testBug721(self):
        obj = QFile(self.filename)
        obj.open(QIODevice.ReadOnly)
        try:
            memory = obj.map(0, 1)
            self.assertEqual(len(memory), 1)
            self.assertEqual(memory[0], ord('a'))
            # now memory points to wild bytes... :-)
            # uncommenting this must cause a segfault.
            # self.assertEqual(memory[0], 'a')
        finally:
            obj.unmap(memory)
            obj.close()

    def testQSaveFile(self):
        dir = QTemporaryDir(QDir.tempPath() + "/XXXXXX.dir")
        self.assertTrue(dir.isValid())
        saveFile = QSaveFile(dir.path() + "/test.dat")
        self.assertTrue(saveFile.open(QIODevice.WriteOnly))
        saveFile.write(bytes("Test", "UTF-8"))
        self.assertTrue(saveFile.commit())
        self.assertTrue(os.path.exists(QDir.toNativeSeparators(saveFile.fileName())))


class GetCharTestPath(GetCharTest):
    # PYSIDE-1499: Do the same with Path objects

    def setUp(self):
        '''Acquire resources'''
        handle, filename = tempfile.mkstemp()
        self.filename = Path(filename)
        os.write(handle, bytes('a', "UTF-8"))
        os.close(handle)


class DirPath(unittest.TestCase):
    # PYSIDE-1499: Test QDir with Path objects
    def testQDirPath(self):
        test_path = Path("some") / "dir"
        qdir1 = QDir(os.fspath(test_path))
        qdir2 = QDir(test_path)
        self.assertEqual(qdir1, qdir2)


if __name__ == '__main__':
    unittest.main()
