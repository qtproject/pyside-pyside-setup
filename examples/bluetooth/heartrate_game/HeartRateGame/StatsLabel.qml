// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick

Item {
    height: GameSettings.fieldHeight
    width: parent.width

    property alias title: leftText.text
    property alias value: rightText.text

    Text {
        id: leftText
        anchors.left: parent.left
        height: parent.height
        width: parent.width * 0.45
        horizontalAlignment: Text.AlignRight
        verticalAlignment: Text.AlignVCenter
        font.pixelSize: GameSettings.mediumFontSize
        color: GameSettings.textColor
    }

    Text {
        id: rightText
        anchors.right: parent.right
        height: parent.height
        width: parent.width * 0.45
        horizontalAlignment: Text.AlignLeft
        verticalAlignment: Text.AlignVCenter
        font.pixelSize: GameSettings.mediumFontSize
        color: GameSettings.textColor
    }
}
