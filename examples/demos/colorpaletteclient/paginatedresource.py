# Copyright (C) 2024 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

import sys
from dataclasses import dataclass
from PySide6.QtCore import (QAbstractListModel, QByteArray,
                            QUrlQuery, Property, Signal, Slot, Qt)
from PySide6.QtQml import QmlAnonymous, QmlElement

from abstractresource import AbstractResource


QML_IMPORT_NAME = "ColorPalette"
QML_IMPORT_MAJOR_VERSION = 1


totalPagesField = "total_pages"
currentPageField = "page"


@dataclass
class ColorUser:
    id: int
    email: str
    avatar: str  # URL


@QmlElement
class ColorUserModel (QAbstractListModel):
    IdRole = Qt.ItemDataRole.UserRole + 1
    EmailRole = Qt.ItemDataRole.UserRole + 2
    AvatarRole = Qt.ItemDataRole.UserRole + 3

    def __init__(self, parent=None):
        super().__init__(parent)
        self._users = []

    def clear(self):
        self.set_data([])

    def set_data(self, json_list):
        if not self._users and not json_list:
            return
        self.beginResetModel()
        self._users.clear()
        for e in json_list:
            self._users.append(ColorUser(int(e["id"]), e["email"], e["avatar"]))
        self.endResetModel()

    def roleNames(self):
        roles = {
            ColorUserModel.IdRole: QByteArray(b'id'),
            ColorUserModel.EmailRole: QByteArray(b'email'),
            ColorUserModel.AvatarRole: QByteArray(b'avatar')
        }
        return roles

    def rowCount(self, index):
        return len(self._users)

    def data(self, index, role):
        if index.isValid():
            d = self._users[index.row()]
            if role == ColorUserModel.IdRole:
                return d.id
            if role == ColorUserModel.EmailRole:
                return d.email
            if role == ColorUserModel.AvatarRole:
                return d.avatar
        return None

    def avatarForEmail(self, email):
        for e in self._users:
            if e.email == email:
                return e.avatar
        return ""


@dataclass
class Color:
    id: int
    color: str
    name: str
    pantone_value: str


@QmlElement
class ColorModel (QAbstractListModel):
    IdRole = Qt.ItemDataRole.UserRole + 1
    ColorRole = Qt.ItemDataRole.UserRole + 2
    NameRole = Qt.ItemDataRole.UserRole + 3
    PantoneValueRole = Qt.ItemDataRole.UserRole + 4

    def __init__(self, parent=None):
        super().__init__(parent)
        self._colors = []

    def clear(self):
        self.set_data([])

    def set_data(self, json_list):
        if not self._colors and not json_list:
            return
        self.beginResetModel()
        self._colors.clear()
        for e in json_list:
            self._colors.append(Color(int(e["id"]), e["color"],
                                      e["name"], e["pantone_value"]))
        self.endResetModel()

    def roleNames(self):
        roles = {
            ColorModel.IdRole: QByteArray(b'color_id'),
            ColorModel.ColorRole: QByteArray(b'color'),
            ColorModel.NameRole: QByteArray(b'name'),
            ColorModel.PantoneValueRole: QByteArray(b'pantone_value')
        }
        return roles

    def rowCount(self, index):
        return len(self._colors)

    def data(self, index, role):
        if index.isValid():
            d = self._colors[index.row()]
            if role == ColorModel.IdRole:
                return d.id
            if role == ColorModel.ColorRole:
                return d.color
            if role == ColorModel.NameRole:
                return d.name
            if role == ColorModel.PantoneValueRole:
                return d.pantone_value
        return None


@QmlAnonymous
class PaginatedResource(AbstractResource):
    """This class manages a simple paginated Crud resource,
       where the resource is a paginated list of JSON items."""

    dataUpdated = Signal()
    pageUpdated = Signal()
    pagesUpdated = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        # The total number of pages as reported by the server responses
        self.m_pages = 0
        # The default page we request if the user hasn't set otherwise
        self.m_currentPage = 1
        self.m_path = ""

    def _clearModel(self):
        pass

    def _populateModel(self, json_list):
        pass

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
        if not reply.isSuccess():
            print("PaginatedResource: ", reply.errorString(), file=sys.stderr)
        (json, error) = reply.readJson()
        if json:
            self.refreshRequestFinished(json)
        else:
            self.refreshRequestFailed()

    def refreshRequestFinished(self, json):
        json_object = json.object()
        self._populateModel(json_object["data"])
        self.m_pages = int(json_object[totalPagesField])
        self.m_currentPage = int(json_object[currentPageField])
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
            self._clearModel()
            self.dataUpdated.emit()

    @Slot("QVariantMap", int)
    def update(self, data, id):
        request = self.m_api.createRequest(f"{self.m_path}/{id}")
        self.m_manager.put(request, self, self.updateReply)

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


@QmlElement
class PaginatedColorUsersResource(PaginatedResource):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_model = ColorUserModel(self)

    @Property(ColorUserModel, constant=True)
    def model(self):
        return self.m_model

    def _clearModel(self):
        self.m_model.clear()

    def _populateModel(self, json_list):
        self.m_model.set_data(json_list)

    @Slot(str, result=str)
    def avatarForEmail(self, email):
        return self.m_model.avatarForEmail(email)


@QmlElement
class PaginatedColorsResource(PaginatedResource):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_model = ColorModel(self)

    @Property(ColorModel, constant=True)
    def model(self):
        return self.m_model

    def _clearModel(self):
        self.m_model.clear()

    def _populateModel(self, json_list):
        self.m_model.set_data(json_list)
