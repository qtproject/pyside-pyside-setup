#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for QtSql database creation, destruction and queries'''

import gc
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel
from PySide6.QtWidgets import QApplication, QWidget


class Foo(QWidget):
    def __init__(self):
        super().__init__()
        self.model = QSqlTableModel()


class SqlDatabaseCreationDestructionAndQueries(unittest.TestCase):
    '''Test cases for QtSql database creation, destruction and queries'''

    def setUp(self):
        # Acquire resources
        self.assertFalse(not QSqlDatabase.drivers(), "installed Qt has no DB drivers")
        self.assertTrue("QSQLITE" in QSqlDatabase.drivers(), "\"QSQLITE\" driver not available in this Qt version")
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName(":memory:")
        self.assertTrue(self.db.open())

    def tearDown(self):
        # Release resources
        self.db.close()
        QSqlDatabase.removeDatabase(":memory:")
        del self.db
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()

    def testTableCreationAndDestruction(self):
        # Test table creation and destruction
        query = QSqlQuery()
        query.exec("CREATE TABLE dummy(id int primary key, dummyfield varchar(20))")
        query.exec("DROP TABLE dummy")
        query.clear()

    def testTableInsertionAndRetrieval(self):
        # Test table creation, insertion and retrieval
        query = QSqlQuery()
        query.exec("CREATE TABLE person(id int primary key, "
                    "firstname varchar(20), lastname varchar(20))")
        query.exec("INSERT INTO person VALUES(101, 'George', 'Harrison')")
        query.prepare("INSERT INTO person (id, firstname, lastname) "
                      "VALUES (:id, :firstname, :lastname)")
        query.bindValue(":id", 102)
        query.bindValue(":firstname", "John")
        query.bindValue(":lastname", "Lennon")
        query.exec()

        lastname = ''
        query.exec("SELECT lastname FROM person where id=101")
        self.assertTrue(query.isActive())
        query.next()
        lastname = query.value(0)
        self.assertEqual(lastname, 'Harrison')

    def testTableModelDeletion(self):
        app = QApplication([])

        bar = Foo()
        model = bar.model
        del bar
        del app
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()


if __name__ == '__main__':
    unittest.main()

