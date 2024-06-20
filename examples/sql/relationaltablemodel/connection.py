# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the relationaltablemodel example from Qt v6.x"""


from PySide6.QtSql import QSqlDatabase


def createConnection():

    def check(func, *args):
        if not func(*args):
            raise ValueError(func.__self__.lastError())
    db = QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName(":memory:")

    check(db.open)
