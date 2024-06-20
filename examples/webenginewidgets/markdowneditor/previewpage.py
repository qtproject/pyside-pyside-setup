# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtGui import QDesktopServices
from PySide6.QtWebEngineCore import QWebEnginePage


class PreviewPage(QWebEnginePage):

    def __init__(self, parent=None):
        super().__init__(parent)

    def acceptNavigationRequest(self, url, type, isMainFrame):
        # Only allow qrc:/index.html.
        if url.scheme() == "qrc":
            return True
        QDesktopServices.openUrl(url)
        return False
