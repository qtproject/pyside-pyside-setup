# Copyright (C) 2024 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtCore import QObject
from PySide6.QtQml import QmlAnonymous


QML_IMPORT_NAME = "ColorPalette"
QML_IMPORT_MAJOR_VERSION = 1


@QmlAnonymous
class AbstractResource(QObject):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_manager = None  # QRestAccessManager
        self.m_api = None  # QNetworkRequestFactory

    def setAccessManager(self, manager):
        self.m_manager = manager

    def setServiceApi(self, serviceApi):
        self.m_api = serviceApi
