# Copyright (C) 2016 Klarälvdalens Datakonsult AB, a KDAB Group company, info@kdab.com,
#   author Milian Wolff <milian.wolff@kdab.com>
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations


import os
import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QDesktopServices
from PySide6.QtNetwork import QHostAddress, QSslSocket
from PySide6.QtCore import (QFile, QFileInfo, QUrl)
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebSockets import QWebSocketServer

from dialog import Dialog
from core import Core
from websocketclientwrapper import WebSocketClientWrapper


if __name__ == '__main__':
    app = QApplication(sys.argv)
    if not QSslSocket.supportsSsl():
        print('The example requires SSL support.')
        sys.exit(-1)
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    js_file_info = QFileInfo(f"{cur_dir}/qwebchannel.js")
    if not js_file_info.exists():
        QFile.copy(":/qtwebchannel/qwebchannel.js",
                   js_file_info.absoluteFilePath())

    # setup the QWebSocketServer
    server = QWebSocketServer("QWebChannel Standalone Example Server",
                              QWebSocketServer.SslMode.NonSecureMode)
    if not server.listen(QHostAddress.SpecialAddress.LocalHost, 12345):
        print("Failed to open web socket server.")
        sys.exit(-1)

    # wrap WebSocket clients in QWebChannelAbstractTransport objects
    client_wrapper = WebSocketClientWrapper(server)

    # setup the channel
    channel = QWebChannel()
    client_wrapper.client_connected.connect(channel.connectTo)

    # setup the UI
    dialog = Dialog()

    # setup the core and publish it to the QWebChannel
    core = Core(dialog)
    channel.registerObject("core", core)

    # open a browser window with the client HTML page
    url = QUrl.fromLocalFile(f"{cur_dir}/index.html")
    QDesktopServices.openUrl(url)

    display_url = url.toDisplayString()
    message = f"Initialization complete, opening browser at {display_url}."
    dialog.display_message(message)
    dialog.show()

    sys.exit(app.exec())
