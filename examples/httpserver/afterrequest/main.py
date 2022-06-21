# Copyright (C) 2020 Mikhail Svetkin <mikhail.svetkin@gmail.com>
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

"""PySide6 port of the /httpserver/afterrequest from from Qt"""

import sys

from PySide6.QtCore import QCoreApplication
from PySide6.QtNetwork import QHostAddress
from PySide6.QtHttpServer import QHttpServer


def route(request):
    return "Hello world"


def after_request(response, request):
    response.setHeader(b"Server", b"Super server!")


if __name__ == '__main__':
    app = QCoreApplication(sys.argv)
    httpServer = QHttpServer()
    httpServer.route("/", route)

    httpServer.afterRequest(after_request)

    port = httpServer.listen(QHostAddress.Any)
    if port == 0:
        print("Server failed to listen on a port.", file=sys.stderr)
        sys.exit(-1)

    print(f"Running on http://127.0.0.1:{port}/ (Press CTRL+\\ to quit)")

    sys.exit(app.exec())
