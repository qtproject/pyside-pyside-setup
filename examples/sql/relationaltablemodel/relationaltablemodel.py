# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the relationaltablemodel example from Qt v6.x"""

import sys

import connection

from PySide6.QtCore import QObject, Qt
from PySide6.QtSql import (QSqlQuery, QSqlRelation, QSqlRelationalDelegate,
                           QSqlRelationalTableModel)
from PySide6.QtWidgets import QApplication, QTableView


def initializeModel(model):

    model.setTable("employee")
    model.setEditStrategy(QSqlRelationalTableModel.OnManualSubmit)
    model.setRelation(2, QSqlRelation("city", "id", "name"))
    model.setRelation(3, QSqlRelation("country", "id", "name"))
    model.setHeaderData(0, Qt.Orientation.Horizontal, QObject().tr("ID"))

    model.setHeaderData(1, Qt.Orientation.Horizontal, QObject().tr("Name"))
    model.setHeaderData(2, Qt.Orientation.Horizontal, QObject().tr("City"))
    model.setHeaderData(3, Qt.Orientation.Horizontal, QObject().tr("Country"))

    model.select()


def createView(title, model):

    table_view = QTableView()
    table_view.setModel(model)
    table_view.setItemDelegate(QSqlRelationalDelegate(table_view))
    table_view.setWindowTitle(title)

    return table_view


def createRelationalTables():

    query = QSqlQuery()

    query.exec("create table employee(id int primary key, name varchar(20), city int, country int)")
    query.exec("insert into employee values(1, 'Espen', 5000, 47)")
    query.exec("insert into employee values(2, 'Harald', 80000, 49)")
    query.exec("insert into employee values(3, 'Sam', 100, 1)")

    query.exec("create table city(id int, name varchar(20))")
    query.exec("insert into city values(100, 'San Jose')")
    query.exec("insert into city values(5000, 'Oslo')")
    query.exec("insert into city values(80000, 'Munich')")

    query.exec("create table country(id int, name varchar(20))")
    query.exec("insert into country values(1, 'USA')")
    query.exec("insert into country values(47, 'Norway')")
    query.exec("insert into country values(49, 'Germany')")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    connection.createConnection()
    createRelationalTables()

    model = QSqlRelationalTableModel()

    initializeModel(model)

    title = "Relational Table Model"

    window = createView(title, model)
    window.resize(600, 200)
    window.show()

    sys.exit(app.exec())
