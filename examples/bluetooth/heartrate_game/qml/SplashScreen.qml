// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick
import "."

Item {
    id: root
    anchors.fill: parent

    property bool appIsReady: false
    property bool splashIsReady: false

    property bool ready: appIsReady && splashIsReady
    onReadyChanged: if (ready) readyToGo();

    signal readyToGo()

    function appReady()
    {
        appIsReady = true
    }

    function errorInLoadingApp()
    {
        Qt.quit()
    }

    Image {
        anchors.centerIn: parent
        width: Math.min(parent.height, parent.width)*0.6
        height: GameSettings.heightForWidth(width, sourceSize)
        source: "images/logo.png"
    }

    Timer {
        id: splashTimer
        interval: 1000
        onTriggered: splashIsReady = true
    }

    Component.onCompleted: splashTimer.start()
}
