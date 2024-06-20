# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

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
        self._oauth2.setClientIdentifier(clientIdentifier)
        self._reply_handler = QOAuthHttpServerReplyHandler(1337, self)
        self._oauth2.setReplyHandler(self._reply_handler)
        self._oauth2.setAuthorizationUrl(QUrl(AUTHORIZATION_URL))
        self._oauth2.setAccessTokenUrl(QUrl(ACCESSTOKEN_URL))
        self._oauth2.setScope("identity read")
        self._permanent = True

        # connect to slots
        self._oauth2.statusChanged.connect(self.status_changed)
        self._oauth2.authorizeWithBrowser.connect(QDesktopServices.openUrl)

        def modify_parameters_function(stage, parameters):
            if stage == QAbstractOAuth.Stage.RequestingAuthorization and self.permanent:
                parameters["duration"] = "permanent"
            return parameters

        self._oauth2.setModifyParametersFunction(modify_parameters_function)

    @Slot()
    def status_changed(self, status):
        if status == QAbstractOAuth.Status.Granted:
            self.authenticated.emit()

    def request_hot_threads(self):
        print("Getting hot threads...")
        return self._oauth2.get(QUrl(HOT_URL))

    @property
    def permanent(self):
        return self._permanent

    @permanent.setter
    def permanent(self, value: bool):
        self._permanent = value

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
        assert document.isObject()
        root_object = document.object()
        data_object = root_object["data"]
        websocketUrl = QUrl(data_object["websocket_url"])
        self.subscribed.emit(websocketUrl)

    def subscribe_to_live_updates(self):
        print("Susbscribing...")
        reply = self._oauth2.get(QUrl(LIVE_THREADS_URL))
        reply.finished.connect(functools.partial(self.reply_finished,
                                                 reply=reply))
