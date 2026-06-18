# Copyright (C) 2024 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtCore import Property, Signal, ClassInfo
from PySide6.QtNetwork import (QNetworkAccessManager, QRestAccessManager,
                               QNetworkRequestFactory, QSslSocket)
from PySide6.QtQml import QmlElement, QPyQmlParserStatus, ListProperty
from abstractresource import AbstractResource

QML_IMPORT_NAME = "ColorPalette"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
@ClassInfo(DefaultProperty="resources")
class RestService(QPyQmlParserStatus):

    urlChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_resources = []
        self.m_qnam = QNetworkAccessManager()
        self.m_qnam.setAutoDeleteReplies(True)
        self.m_manager = QRestAccessManager(self.m_qnam)
        self.m_serviceApi = QNetworkRequestFactory()

    @Property(str, notify=urlChanged)
    def url(self):
        return self.m_serviceApi.baseUrl()

    @url.setter
    def url(self, url):
        if self.m_serviceApi.baseUrl() != url:
            self.m_serviceApi.setBaseUrl(url)
            self.urlChanged.emit()

    @Property(bool, constant=True)
    def sslSupported(self):
        return QSslSocket.supportsSsl()

    def classBegin(self):
        pass

    def componentComplete(self):
        for resource in self.m_resources:
            resource.setAccessManager(self.m_manager)
            resource.setServiceApi(self.m_serviceApi)

    def appendResource(self, r):
        self.m_resources.append(r)

    resources = ListProperty(AbstractResource, appendResource)
