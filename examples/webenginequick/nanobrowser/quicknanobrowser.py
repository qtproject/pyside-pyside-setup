# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

"""PySide6 WebEngine QtQuick 2 Example"""

import os
from PySide6.QtCore import QUrl
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication
from PySide6.QtWebEngineQuick import QtWebEngineQuick


def main():
    QtWebEngineQuick.initialize()
    app = QApplication([])
    engine = QQmlApplicationEngine()
    qml_file_path = os.path.join(os.path.dirname(__file__), 'browser.qml')
    qml_url = QUrl.fromLocalFile(os.path.abspath(qml_file_path))
    engine.load(qml_url)
    app.exec()


if __name__ == '__main__':
    main()
