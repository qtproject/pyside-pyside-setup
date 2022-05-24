# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import sys

from PySide6.QtCore import Qt
from PySide6.QtSql import QSqlQueryModel
from PySide6.QtWidgets import QTableView, QApplication

import createdb
from bookdelegate import BookDelegate

if __name__ == "__main__":
    app = QApplication()
    createdb.init_db()

    model = QSqlQueryModel()
    model.setQuery("select title, author, genre, year, rating from books")

    table = QTableView()
    table.setModel(model)
    table.setItemDelegate(BookDelegate())
    table.resize(800, 600)
    table.show()

    sys.exit(app.exec())
