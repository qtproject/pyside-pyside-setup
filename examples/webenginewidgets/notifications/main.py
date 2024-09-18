# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 WebEngineWidgets Notifications Example"""

import sys
from pathlib import Path

from PySide6.QtCore import QUrl, QCoreApplication
from PySide6.QtWidgets import QApplication
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtGui import QDesktopServices

from notificationpopup import NotificationPopup


class WebEnginePage(QWebEnginePage):
    def __init__(self, parent):
        super().__init__(parent)

    def acceptNavigationRequest(self, url: QUrl, *_):
        if url.scheme != "https":
            return True
        QDesktopServices.openUrl(url)
        return False


if __name__ == '__main__':

    src_dir = Path(__file__).resolve().parent
    QCoreApplication.setOrganizationName("QtProject")
    app = QApplication(sys.argv)
    view = QWebEngineView()

    # set custom page to open all page's links for https scheme in system browser
    view.setPage(WebEnginePage(view))

    def set_feature_permission(origin: QUrl, feature: QWebEnginePage.Feature):
        if feature != QWebEnginePage.Feature.Notifications:
            return

        view.page().setFeaturePermission(origin, feature,
                                         QWebEnginePage.PermissionPolicy.PermissionGrantedByUser)

    view.page().featurePermissionRequested.connect(set_feature_permission)
    profile = view.page().profile()
    popup = NotificationPopup(view)

    def presentNotification(notification):
        popup.present(notification)

    profile.setNotificationPresenter(presentNotification)
    view.resize(640, 480)
    view.show()
    view.setUrl(QUrl.fromLocalFile(src_dir / "resources" / "index.html"))

    sys.exit(app.exec())
