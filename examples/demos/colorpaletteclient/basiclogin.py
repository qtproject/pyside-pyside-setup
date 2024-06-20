# Copyright (C) 2024 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

import sys
from functools import partial
from dataclasses import dataclass

from PySide6.QtCore import Property, Signal, Slot
from PySide6.QtNetwork import QHttpHeaders
from PySide6.QtQml import QmlElement

from abstractresource import AbstractResource


tokenField = "token"
emailField = "email"
idField = "id"


QML_IMPORT_NAME = "ColorPalette"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
class BasicLogin(AbstractResource):
    @dataclass
    class User:
        email: str
        token: bytes
        id: int

    userChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_user = None
        self.m_loginPath = ""
        self.m_logoutPath = ""
        self.m_user = None

    @Property(str, notify=userChanged)
    def user(self):
        return self.m_user.email if self.m_user else ""

    @Property(bool, notify=userChanged)
    def loggedIn(self):
        return bool(self.m_user)

    @Property(str)
    def loginPath(self):
        return self.m_loginPath

    @loginPath.setter
    def loginPath(self, p):
        self.m_loginPath = p

    @Property(str)
    def logoutPath(self):
        return self.m_logoutPath

    @logoutPath.setter
    def logoutPath(self, p):
        self.m_logoutPath = p

    @Slot("QVariantMap")
    def login(self, data):
        request = self.m_api.createRequest(self.m_loginPath)
        self.m_manager.post(request, data, self, partial(self.loginReply, data))

    def loginReply(self, data, reply):
        self.m_user = None
        if not reply.isSuccess():
            print("login: ", reply.errorString(), file=sys.stderr)
        (json, error) = reply.readJson()
        if json and json.isObject():
            json_object = json.object()
            token = json_object.get(tokenField)
            if token:
                email = data[emailField]
                token = json_object[tokenField]
                id = data[idField]
                self.m_user = BasicLogin.User(email, token, id)

        headers = QHttpHeaders()
        headers.append("token", self.m_user.token if self.m_user else "")
        self.m_api.setCommonHeaders(headers)
        self.userChanged.emit()

    @Slot()
    def logout(self):
        request = self.m_api.createRequest(self.m_logoutPath)
        self.m_manager.post(request, b"", self, self.logoutReply)

    def logoutReply(self, reply):
        if reply.isSuccess():
            self.m_user = None
            self.m_api.clearCommonHeaders()  # clears 'token' header
            self.userChanged.emit()
        else:
            print("logout: ", reply.errorString(), file=sys.stderr)
