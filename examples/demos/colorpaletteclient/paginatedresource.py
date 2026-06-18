# Copyright (C) 2024 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

import sys
from PySide6.QtCore import (QUrlQuery, Property, Signal, Slot)
from PySide6.QtNetwork import QNetworkReply
from PySide6.QtQml import QmlElement

from abstractresource import AbstractResource


QML_IMPORT_NAME = "ColorPalette"
QML_IMPORT_MAJOR_VERSION = 1


totalPagesField = "total_pages"
currentPageField = "page"


@QmlElement
class PaginatedResource(AbstractResource):
    """This class manages a simple paginated Crud resource,
       where the resource is a paginated list of JSON items."""

    dataUpdated = Signal()
    pageUpdated = Signal()
    pagesUpdated = Signal()
    errorOccurred = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        # The total number of pages as reported by the server responses
        self.m_pages = 0
        # The default page we request if the user hasn't set otherwise
        self.m_currentPage = 1
        self.m_path = ""
        self._data = []

    @Property(str)
    def path(self):
        return self.m_path

    @path.setter
    def path(self, p):
        self.m_path = p

    @Property(int, notify=pagesUpdated)
    def pages(self):
        return self.m_pages

    @Property(int, notify=pageUpdated)
    def page(self):
        return self.m_currentPage

    @page.setter
    def page(self, page):
        if self.m_currentPage == page or page < 1:
            return
        self.m_currentPage = page
        self.pageUpdated.emit()
        self.refreshCurrentPage()

    @Slot()
    def refreshCurrentPage(self):
        query = QUrlQuery()
        query.addQueryItem("page", str(self.m_currentPage))
        request = self.m_api.createRequest(self.m_path, query)
        self.m_manager.get(request, self, self.refreshCurrentPageReply)

    def refreshCurrentPageReply(self, reply):
        error = ""
        if reply.isSuccess():
            (json, jsonError) = reply.readJson()
            if json:
                self.refreshRequestFinished(json)
            else:
                error = jsonError.errorString()
        else:
            error = (reply.errorString() if reply.error() != QNetworkReply.NetworkError.NoError
                     else f"HTTP status: {reply.httpStatus()}")
        if error:
            url = reply.networkReply().url().toString()
            print(f'PaginatedResource: request "{url}" failed: "{error}"', file=sys.stderr)
            self.errorOccurred.emit(error)
            self.refreshRequestFailed()

    def refreshRequestFinished(self, json):
        json_object = json.object()
        data = json_object.get("data")
        totalPages = json_object.get(totalPagesField)
        currentPage = json_object.get(currentPageField)
        self._data = data if data else []
        self.m_pages = int(totalPages) if totalPages else 1
        self.m_currentPage = int(currentPage) if currentPage else 1
        self.pageUpdated.emit()
        self.pagesUpdated.emit()
        self.dataUpdated.emit()

    def refreshRequestFailed(self):
        if self.m_currentPage != 1:
            # A failed refresh. If we weren't on page 1, try that.
            # Last resource on currentPage might have been deleted, causing a failure
            self.setPage(1)
        else:
            # Refresh failed and we we're already on page 1 => clear data
            self.m_pages = 0
            self.pagesUpdated.emit()
            self._data = []
            self.dataUpdated.emit()

    @Slot("QVariantMap", int)
    def update(self, data, id):
        request = self.m_api.createRequest(f"{self.m_path}/{id}")
        self.m_manager.put(request, data, self, self.updateReply)

    def updateReply(self, reply):
        if reply.isSuccess():
            self.refreshCurrentPage()

    @Slot("QVariantMap")
    def add(self, data):
        request = self.m_api.createRequest(self.m_path)
        self.m_manager.post(request, data, self, self.updateReply)

    @Slot(int)
    def remove(self, id):
        request = self.m_api.createRequest(f"{self.m_path}/{id}")
        self.m_manager.deleteResource(request, self, self.updateReply)

    @Property("QList<QJsonObject>", notify=dataUpdated, final=True)
    def data(self):
        return self._data
