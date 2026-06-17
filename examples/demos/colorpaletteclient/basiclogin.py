# Copyright (C) 2024 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

import sys
from functools import partial
from dataclasses import dataclass

from PySide6.QtCore import Slot
from PySide6.QtNetwork import QHttpHeaders
from PySide6.QtQml import QmlElement
from PySide6.QtQmlFeatures import auto_properties, computed

from abstractresource import AbstractResource


tokenField = "token"
emailField = "email"
idField = "id"


QML_IMPORT_NAME = "ColorPalette"
QML_IMPORT_MAJOR_VERSION = 1


# @auto_properties builds the loginPath/logoutPath/userRecord Q_PROPERTYs from
# the plain __init__ assignments, and turns the @computed methods into
# read-only properties. Whenever userRecord changes, "user" and "loggedIn" are
# recomputed and their notify signals fire, so the QML bindings refresh - no
# manual userChanged signal or emits required.
@QmlElement
@auto_properties
class BasicLogin(AbstractResource):
    @dataclass
    class User:
        email: str
        token: bytes
        id: int

    def __init__(self, parent=None):
        super().__init__(parent)
        self.loginPath = ""
        self.logoutPath = ""
        self.userRecord = None

    @computed("userRecord")
    def user(self) -> str:
        return self.userRecord.email if self.userRecord else ""

    @computed("userRecord")
    def loggedIn(self) -> bool:
        return bool(self.userRecord)

    @Slot("QVariantMap")
    def login(self, data):
        request = self.m_api.createRequest(self.loginPath)
        self.m_manager.post(request, data, self, partial(self.loginReply, data))

    def loginReply(self, data, reply):
        record = None
        if not reply.isSuccess():
            print("login: ", reply.errorString(), file=sys.stderr)
        (json, error) = reply.readJson()
        if json and json.isObject():
            json_object = json.object()
            if token := json_object.get(tokenField):
                email = data[emailField]
                token = json_object[tokenField]
                id = data[idField]
                record = BasicLogin.User(email, token, id)

        headers = QHttpHeaders()
        headers.append("token", record.token if record else "")
        self.m_api.setCommonHeaders(headers)
        self.userRecord = record

    @Slot()
    def logout(self):
        request = self.m_api.createRequest(self.logoutPath)
        self.m_manager.post(request, b"", self, self.logoutReply)

    def logoutReply(self, reply):
        if reply.isSuccess():
            self.userRecord = None
            self.m_api.clearCommonHeaders()  # clears 'token' header
        else:
            print("logout: ", reply.errorString(), file=sys.stderr)
