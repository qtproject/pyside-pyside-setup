# Copyright (C) 2017 Klarälvdalens Datakonsult AB, a KDAB Group company, info@kdab.com, author Milian Wolff <milian.wolff@kdab.com>
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtWebChannel import QWebChannelAbstractTransport
from PySide6.QtCore import QByteArray, QJsonDocument, Slot


class WebSocketTransport(QWebChannelAbstractTransport):
    """QWebChannelAbstractSocket implementation using a QWebSocket internally.

        The transport delegates all messages received over the QWebSocket over
        its textMessageReceived signal. Analogously, all calls to
        sendTextMessage will be sent over the QWebSocket to the remote client.
    """

    def __init__(self, socket):
        """Construct the transport object and wrap the given socket.
           The socket is also set as the parent of the transport object."""
        super().__init__(socket)
        self._socket = socket
        self._socket.textMessageReceived.connect(self.text_message_received)
        self._socket.disconnected.connect(self._disconnected)

    def __del__(self):
        """Destroys the WebSocketTransport."""
        self._socket.deleteLater()

    def _disconnected(self):
        self.deleteLater()

    def sendMessage(self, message):
        """Serialize the JSON message and send it as a text message via the
           WebSocket to the client."""
        doc = QJsonDocument(message)
        json_message = str(doc.toJson(QJsonDocument.Compact), "utf-8")
        self._socket.sendTextMessage(json_message)

    @Slot(str)
    def text_message_received(self, message_data_in):
        """Deserialize the stringified JSON messageData and emit
           messageReceived."""
        message_data = QByteArray(bytes(message_data_in, encoding='utf8'))
        message = QJsonDocument.fromJson(message_data)
        if message.isNull():
            print("Failed to parse text message as JSON object:", message_data)
            return
        if not message.isObject():
            print("Received JSON message that is not an object: ", message_data)
            return
        self.messageReceived.emit(message.object(), self)
