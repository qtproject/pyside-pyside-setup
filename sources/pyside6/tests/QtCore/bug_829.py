# Copyright (C) 2022 The Qt Company Ltd.
# Copyright (C) 2011 Thomas Perl <thp.io/about>
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

# Test case for PySide bug 829

import gc
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QDir, QSettings, QTemporaryFile


class QVariantConversions(unittest.TestCase):

    _confFileName = None

    def testDictionary(self):
        confFile = QTemporaryFile(QDir.tempPath() + '/pysidebug829_XXXXXX.ini')
        confFile.setAutoRemove(False)
        self.assertTrue(confFile.open())
        confFile.close()
        self._confFileName = confFile.fileName()
        del confFile
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        s = QSettings(self._confFileName, QSettings.IniFormat)
        self.assertEqual(s.status(), QSettings.NoError)
        # Save value
        s.setValue('x', {1: 'a'})
        s.sync()
        self.assertEqual(s.status(), QSettings.NoError)
        del s
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()

        # Restore value
        s = QSettings(self._confFileName, QSettings.IniFormat)
        self.assertEqual(s.status(), QSettings.NoError)
        self.assertEqual(s.value('x'), {1: 'a'})

    def __del__(self):
        if self._confFileName is not None:
            os.unlink(QDir.toNativeSeparators(self._confFileName))


if __name__ == '__main__':
    unittest.main()
