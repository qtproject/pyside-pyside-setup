// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: root
    property bool checked: false
    property alias routeInstruction: instructionLabel
    property alias routeDistance: distanceLabel
    property alias routeIndex: indexLabel

    width: appWindow.width
    height: indexLabel.height * 2

    RowLayout {
        spacing: 10
        anchors.left: parent.left
        anchors.leftMargin: 30
        anchors.verticalCenter: parent.verticalCenter
        Label {
            id: indexLabel
        }
        Label {
            id: instructionLabel
            wrapMode: Text.Wrap
        }
        Label {
            id: distanceLabel
        }
    }

    Rectangle {
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.margins: 15
        height: 1
        color: "#46a2da"
    }
}
