// Copyright (C) 2018 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick
import QtQuick.Window
import QtWebEngine

Window {
    width: 1024
    height: 768
    visible: true
    WebEngineView {
        anchors.fill: parent
        url: "https://www.qt.io"
    }
}
