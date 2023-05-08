// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick

Item {
    id: page

    property string errorMessage: ""
    property string infoMessage: ""
    property real messageHeight: msg.height
    property bool hasError: errorMessage != ""
    property bool hasInfo: infoMessage != ""

    Rectangle {
        id: msg
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: GameSettings.fieldHeight
        color: page.hasError ? GameSettings.errorColor : GameSettings.infoColor
        visible: page.hasError || page.hasInfo

        Text {
            id: error
            anchors.fill: parent
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            minimumPixelSize: 5
            font.pixelSize: GameSettings.smallFontSize
            fontSizeMode: Text.Fit
            color: GameSettings.textColor
            text: page.hasError ? page.errorMessage : page.infoMessage
        }
    }
}
