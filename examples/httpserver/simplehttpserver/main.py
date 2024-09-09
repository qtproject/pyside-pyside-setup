# Copyright (C) 2020 Mikhail Svetkin <mikhail.svetkin@gmail.com>
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the /httpserver/afterrequest from from Qt"""

import sys

from PySide6.QtCore import QCoreApplication
from PySide6.QtNetwork import QHttpHeaders, QTcpServer
from PySide6.QtHttpServer import QHttpServer


def route(request):
    return "Hello world"


def after_request(request, response):
    headers = response.headers()
    headers.append(QHttpHeaders.WellKnownHeader.WWWAuthenticate,
                   'Basic realm="Simple example", charset="UTF-8"')
    response.setHeaders(headers)


if __name__ == '__main__':
    app = QCoreApplication(sys.argv)
    httpServer = QHttpServer()
    httpServer.route("/", route)

    httpServer.addAfterRequestHandler(httpServer, after_request)

    tcpServer = QTcpServer()
    if not tcpServer.listen() or not httpServer.bind(tcpServer):
        print("Server failed to listen on a port.", file=sys.stderr)
        sys.exit(-1)
    port = tcpServer.serverPort()

    print(f"Running on http://127.0.0.1:{port}/ (Press CTRL+\\ to quit)")

    sys.exit(app.exec())
