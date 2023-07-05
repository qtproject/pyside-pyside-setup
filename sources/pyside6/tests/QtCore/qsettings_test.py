# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for QDate'''

import gc
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QDir, QSettings, QTemporaryDir, QByteArray


class TestQSettings(unittest.TestCase):
    def testConversions(self):
        file = Path(__file__).resolve().parent / 'qsettings_test.ini'
        self.assertTrue(file.is_file())
        file_path = QDir.fromNativeSeparators(os.fspath(file))
        settings = QSettings(file_path, QSettings.IniFormat)

        r = settings.value('var1')
        self.assertEqual(type(r), list)

        r = settings.value('var2')
        self.assertEqual(type(r), str)

        r = settings.value('var2', type=list)
        self.assertEqual(type(r), list)

        # Test mixed conversions
        ba = QByteArray("hello".encode("utf-8"))

        r = settings.value("test", ba, type=QByteArray)
        self.assertEqual(type(r), QByteArray)

        r = settings.value("test", ba, type=str)
        self.assertEqual(type(r), str)

        # Test invalid conversions
        with self.assertRaises(TypeError):
            r = settings.value("test", ba, type=dict)

    def testDefaultValueConversion(self):
        temp_dir = QDir.tempPath()
        dir = QTemporaryDir(f'{temp_dir}/qsettings_XXXXXX')
        self.assertTrue(dir.isValid())
        file_name = dir.filePath('foo.ini')
        settings = QSettings(file_name, QSettings.IniFormat)
        sample_list = ["a", "b"]
        string_list_of_empty = [""]
        settings.setValue('zero_value', 0)
        settings.setValue('empty_list', [])
        settings.setValue('some_strings', sample_list)
        settings.setValue('string_list_of_empty', string_list_of_empty)
        settings.setValue('bool1', False)
        settings.setValue('bool2', True)
        del settings
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()

        # Loading values already set
        settings = QSettings(file_name, QSettings.IniFormat)

        # Getting value that doesn't exist
        r = settings.value("variable")
        self.assertEqual(type(r), type(None))

        r = settings.value("variable", type=list)
        self.assertEqual(type(r), list)
        self.assertEqual(len(r), 0)

        # Handling zero value
        r = settings.value('zero_value')
        self.assertEqual(type(r), int)

        r = settings.value('zero_value', type=int)
        self.assertEqual(type(r), int)

        # Empty list
        r = settings.value('empty_list')
        self.assertTrue(len(r) == 0)
        self.assertEqual(type(r), list)

        r = settings.value('empty_list', type=list)
        self.assertTrue(len(r) == 0)
        self.assertEqual(type(r), list)

        r = settings.value('some_strings')
        self.assertEqual(r, sample_list)

        r = settings.value('some_strings', type=list)
        self.assertEqual(r, sample_list)

        r = settings.value('string_list_of_empty', type=list)
        self.assertEqual(r, string_list_of_empty)

        # Booleans
        r = settings.value('bool1')
        self.assertEqual(type(r), bool)

        r = settings.value('bool2')
        self.assertEqual(type(r), bool)

        r = settings.value('bool1', type=bool)
        self.assertEqual(type(r), bool)

        r = settings.value('bool2', type=int)
        self.assertEqual(type(r), int)

        r = settings.value('bool2', type=bool)
        self.assertEqual(type(r), bool)

        # Not set variable, but with default value
        r = settings.value('lala', 22, type=bytes)
        self.assertEqual(type(r), bytes)

        r = settings.value('lala', 22, type=int)
        self.assertEqual(type(r), int)

        r = settings.value('lala', 22, type=float)
        self.assertEqual(type(r), float)


if __name__ == '__main__':
    unittest.main()
