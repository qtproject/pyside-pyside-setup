# Copyright (C) 2017 Ford Motor Company
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the remoteobjects/modelviewclient example from Qt v5.x"""

import sys

from PySide6.QtCore import QUrl
from PySide6.QtWidgets import (QApplication, QTreeView)
from PySide6.QtRemoteObjects import QRemoteObjectNode

if __name__ == '__main__':
    app = QApplication(sys.argv)
    node = QRemoteObjectNode(QUrl("local:registry"))
    node.setHeartbeatInterval(1000)
    view = QTreeView()
    view.setWindowTitle("RemoteView")
    view.resize(640, 480)
    model = node.acquireModel("RemoteModel")
    view.setModel(model)
    view.show()

    sys.exit(app.exec())
