# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

import datetime
import logging

from PySide6.QtCore import Qt, Slot
from PySide6.QtSql import QSqlDatabase, QSqlQuery, QSqlRecord, QSqlTableModel
from PySide6.QtQml import QmlElement

table_name = "Conversations"
QML_IMPORT_NAME = "ChatModel"
QML_IMPORT_MAJOR_VERSION = 1


def createTable():
    if table_name in QSqlDatabase.database().tables():
        return

    query = QSqlQuery()
    if not query.exec_(
        """
        CREATE TABLE IF NOT EXISTS 'Conversations' (
            'author' TEXT NOT NULL,
            'recipient' TEXT NOT NULL,
            'timestamp' TEXT NOT NULL,
            'message' TEXT NOT NULL,
        FOREIGN KEY('author') REFERENCES Contacts ( name ),
        FOREIGN KEY('recipient') REFERENCES Contacts ( name )
        )
        """
    ):
        logging.error("Failed to query database")

    # This adds the first message from the Bot
    # and further development is required to make it interactive.
    query.exec_(
        """
        INSERT INTO Conversations VALUES(
            'machine', 'Me', '2019-01-07T14:36:06', 'Hello!'
        )
        """
    )
    logging.info(query)


@QmlElement
class SqlConversationModel(QSqlTableModel):
    def __init__(self, parent=None):
        super(SqlConversationModel, self).__init__(parent)

        createTable()
        self.setTable(table_name)
        self.setSort(2, Qt.DescendingOrder)
        self.setEditStrategy(QSqlTableModel.OnManualSubmit)
        self.recipient = ""

        self.select()
        logging.debug("Table was loaded successfully.")

    def data(self, index, role):
        if role < Qt.UserRole:
            return QSqlTableModel.data(self, index, role)

        sql_record = QSqlRecord()
        sql_record = self.record(index.row())

        return sql_record.value(role - Qt.UserRole)

    def roleNames(self):
        """Converts dict to hash because that's the result expected
        by QSqlTableModel"""

        return {int(Qt.UserRole): b"author",
                Qt.UserRole + 1: b"recipient",
                Qt.UserRole + 2: b"timestamp",
                Qt.UserRole + 3: b"message"}

    # This is a workaround because PySide doesn't provide Q_INVOKABLE
    # So we declare this as a Slot to be able to call it  from QML
    @Slot(str, str, str)
    def send_message(self, recipient, message, author):
        timestamp = datetime.datetime.now()

        new_record = self.record()
        new_record.setValue("author", author)
        new_record.setValue("recipient", recipient)
        new_record.setValue("timestamp", str(timestamp))
        new_record.setValue("message", message)

        logging.debug(f'Message: "{message}" \n Received by: "{recipient}"')

        if not self.insertRecord(self.rowCount(), new_record):
            logging.error("Failed to send message: {self.lastError().text()}")
            return

        self.submitAll()
        self.select()
