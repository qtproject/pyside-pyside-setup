# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

import functools
from PySide6.QtCore import (QAbstractTableModel, QJsonDocument, QModelIndex,
                            Qt, Signal, Slot)
from PySide6.QtNetwork import QNetworkReply

from redditwrapper import RedditWrapper


class RedditModel(QAbstractTableModel):

    error = Signal(str)

    def __init__(self, client_id):
        super().__init__()
        self._reddit_wrapper = RedditWrapper(client_id)
        self._reddit_wrapper.authenticated.connect(self.update)
        self._live_thread_reply = None
        self._threads = []
        self.grant()

    def rowCount(self, parent):
        return len(self._threads)

    def columnCount(self, parent):
        return 1 if self._threads else 0

    def data(self, index, role):
        if not index.isValid():
            return None
        if role == Qt.ItemDataRole.DisplayRole:
            children_object = self._threads[index.row()]
            data_object = children_object["data"]
            return data_object["title"]
        return None

    def grant(self):
        self._reddit_wrapper.grant()

    @Slot(QNetworkReply)
    def reply_finished(self, reply):
        reply.deleteLater()
        if reply.error() != QNetworkReply.NoError:
            error = reply.errorString()
            print(f"Reddit error: {error}")
            self.error.emit(error)
            return
        json = reply.readAll()
        document = QJsonDocument.fromJson(json)
        root_object = document.object()
        kind = root_object["kind"]
        assert kind == "Listing"
        data_object = root_object["data"]
        children_array = data_object["children"]
        if not children_array:
            return

        self.beginInsertRows(QModelIndex(), len(self._threads),
                             len(children_array) + len(self._threads) - 1)
        for childValue in children_array:
            self._threads.append(childValue)
        self.endInsertRows()

    @Slot()
    def update(self):
        reply = self._reddit_wrapper.request_hot_threads()
        reply.finished.connect(functools.partial(self.reply_finished,
                                                 reply=reply))
