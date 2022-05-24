# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import sys

from PySide6.QtSql import QSqlQueryModel
from PySide6.QtWidgets import QTableView, QApplication

import createdb

if __name__ == "__main__":
    app = QApplication()
    createdb.init_db()

    model = QSqlQueryModel()
    model.setQuery("select * from books")

    table_view = QTableView()
    table_view.setModel(model)
    table_view.resize(800, 600)
    table_view.show()
    sys.exit(app.exec())
