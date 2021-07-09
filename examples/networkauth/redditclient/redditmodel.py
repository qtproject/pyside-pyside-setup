#############################################################################
##
## Copyright (C) 2021 The Qt Company Ltd.
## Contact: http://www.qt.io/licensing/
##
## This file is part of the Qt for Python examples of the Qt Toolkit.
##
## $QT_BEGIN_LICENSE:BSD$
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of The Qt Company Ltd nor the names of its
##     contributors may be used to endorse or promote products derived
##     from this software without specific prior written permission.
##
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
## $QT_END_LICENSE$
##
#############################################################################

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
        if role == Qt.DisplayRole:
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
        assert(kind == "Listing")
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
