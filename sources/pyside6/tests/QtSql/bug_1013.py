# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QCoreApplication, QTimer
from PySide6.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel


class TestBug1013 (unittest.TestCase):

    def someSlot(self, row, record):
        record.setValue(0, 2)
        self._wasCalled = True

    def testIt(self):
        app = QCoreApplication([])
        db = QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName(':memory:')
        db.open()
        query = QSqlQuery()
        query.exec('CREATE TABLE "foo" (id INT);')
        model = QSqlTableModel()
        model.setTable('foo')

        self._wasCalled = False
        model.primeInsert.connect(self.someSlot)
        model.select()
        QTimer.singleShot(0, lambda: model.insertRow(0) and app.quit())
        app.exec()
        self.assertTrue(self._wasCalled)
        self.assertEqual(model.data(model.index(0, 0)), 2)


if __name__ == "__main__":
    unittest.main()
