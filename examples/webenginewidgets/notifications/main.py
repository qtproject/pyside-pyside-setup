#############################################################################
##
## Copyright (C) 2022 The Qt Company Ltd.
## Contact: https://www.qt.io/licensing/
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
        if feature != QWebEnginePage.Notifications:
            return

        view.page().setFeaturePermission(origin, feature, QWebEnginePage.PermissionGrantedByUser)

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
