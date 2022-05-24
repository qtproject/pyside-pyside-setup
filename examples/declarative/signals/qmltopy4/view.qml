// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick

Rectangle {
    id: page

    width: 500; height: 200
    color: "lightgray"

    Rectangle {
        id: button
        width: 150; height: 40
        color: "darkgray"
        anchors.horizontalCenter: page.horizontalCenter
        anchors.verticalCenter: page.verticalCenter
        MouseArea {
            id: buttonMouseArea
            objectName: "buttonMouseArea"
            anchors.fill: parent
        }
        Text {
            id: buttonText
            text: "Press me!"
            anchors.horizontalCenter: button.horizontalCenter
            anchors.verticalCenter: button.verticalCenter
            font.pointSize: 16
        }
    }
}
