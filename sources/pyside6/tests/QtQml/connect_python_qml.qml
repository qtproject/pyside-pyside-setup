// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import QtQuick 2.0

Rectangle {
    id: page
    width: 500; height: 200
    color: "lightgray"

    Rectangle {
        id: button
        width: 150; height: 40
        color: "darkgray"
        anchors.horizontalCenter: page.horizontalCenter
        y: 150
        MouseArea {
            id: buttonMouseArea
            objectName: "buttonMouseArea"
            anchors.fill: parent
        }
    }
}
