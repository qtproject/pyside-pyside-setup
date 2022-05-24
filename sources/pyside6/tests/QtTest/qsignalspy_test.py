# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''QtTest QSignalSpy'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import Qt, QObject, SIGNAL
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtTest import QTest, QSignalSpy

from helper.usesqapplication import UsesQApplication


class QSignalSpyTest(UsesQApplication):

    def setUp(self):
        super().setUp()
        self._model = QStandardItemModel(0, 1)
        self._model.appendRow(QStandardItem('text1'))

    def testStringBased(self):
        s = SIGNAL('dataChanged(QModelIndex,QModelIndex,QList<int>)')
        spy = QSignalSpy(self._model, s)
        self._model.item(0, 0).setText('text2')
        self.assertEqual(spy.count(), 1)

    def testSignal(self):
        spy = QSignalSpy(self._model.dataChanged)
        self._model.item(0, 0).setText('text3')
        self.assertEqual(spy.count(), 1)


if __name__ == '__main__':
    unittest.main()
