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

from PySide6.QtCore import QJsonDocument, QObject, QUrl, Signal, Slot
from PySide6.QtGui import QDesktopServices
from PySide6.QtNetwork import QNetworkReply
from PySide6.QtNetworkAuth import (QAbstractOAuth,
                                   QOAuth2AuthorizationCodeFlow,
                                   QOAuthHttpServerReplyHandler)


AUTHORIZATION_URL = "https://www.reddit.com/api/v1/authorize"
ACCESSTOKEN_URL = "https://www.reddit.com/api/v1/access_token"


NEW_URL = "https://oauth.reddit.com/new"
HOT_URL = "https://oauth.reddit.com/hot"
LIVE_THREADS_URL = "https://oauth.reddit.com/live/XXXX/about.json"


class RedditWrapper(QObject):

    authenticated = Signal()
    subscribed = Signal(QUrl)

    def __init__(self, clientIdentifier, parent=None):
        super().__init__(parent)

        self._oauth2 = QOAuth2AuthorizationCodeFlow()
        self._oauth2.statusChanged.connect(self.status_changed)
        self._oauth2.authorizeWithBrowser.connect(QDesktopServices.openUrl)
        self._oauth2.setClientIdentifier(clientIdentifier)
        self._reply_handler = QOAuthHttpServerReplyHandler(1337, self)
        self._oauth2.setReplyHandler(self._reply_handler)
        self._oauth2.setAuthorizationUrl(QUrl(AUTHORIZATION_URL))
        self._oauth2.setAccessTokenUrl(QUrl(ACCESSTOKEN_URL))
        self._oauth2.setScope("identity read")

    @Slot()
    def status_changed(self, status):
        if status == QAbstractOAuth.Status.Granted:
            self.authenticated.emit()

    def request_hot_threads(self):
        print("Getting hot threads...")
        return self._oauth2.get(QUrl(HOT_URL))

    def grant(self):
        self._oauth2.grant()

    @Slot(QNetworkReply)
    def reply_finished(self, reply):
        print('RedditWrapper.reply_finished()', reply.error())
        reply.deleteLater()
        if reply.error() != QNetworkReply.NoError:
            error = reply.errorString()
            print(f"Reddit error: {error}")
            return

        json = reply.readAll()
        document = QJsonDocument.fromJson(json)
        assert(document.isObject())
        root_object = document.object()
        data_object = root_object["data"]
        websocketUrl = QUrl(data_object["websocket_url"])
        self.subscribed.emit(websocketUrl)

    def subscribe_to_live_updates(self):
        print("Susbscribing...")
        reply = self._oauth2.get(QUrl(LIVE_THREADS_URL))
        reply.finished.connect(functools.partial(self.reply_finished,
                                                 reply=reply))
