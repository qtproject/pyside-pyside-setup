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
    property int iconType: BluetoothBaseClass.IconNone

    function iconTypeToName(icon: int) : string {
        switch (icon) {
        case BluetoothBaseClass.IconNone: return ""
        case BluetoothBaseClass.IconBluetooth: return "images/bluetooth.svg"
        case BluetoothBaseClass.IconError: return "images/alert.svg"
        case BluetoothBaseClass.IconProgress: return "images/progress.svg"
        case BluetoothBaseClass.IconSearch: return "images/search.svg"
        }
    }

    Rectangle {
        id: msg
        anchors {
            top: parent.top
            left: parent.left
            right: parent.right
            topMargin: GameSettings.fieldMargin * 0.5
            leftMargin: GameSettings.fieldMargin
            rightMargin: GameSettings.fieldMargin
        }
        height: GameSettings.fieldHeight
        radius: GameSettings.buttonRadius
        color: page.hasError ? GameSettings.errorColor : "transparent"
        visible: page.hasError || page.hasInfo
        border {
            width: 1
            color: page.hasError ? GameSettings.errorColor : GameSettings.infoColor
        }

        Image {
            id: icon
            readonly property int imgSize: GameSettings.fieldHeight * 0.5
            anchors {
                left: parent.left
                leftMargin: GameSettings.fieldMargin * 0.5
                verticalCenter: parent.verticalCenter
            }
            visible: source.toString() !== ""
            source: page.iconTypeToName(page.iconType)
            sourceSize.width: imgSize
            sourceSize.height: imgSize
            fillMode: Image.PreserveAspectFit
        }

        Text {
            id: error
            anchors {
                fill: parent
                leftMargin: GameSettings.fieldMargin + icon.width
                rightMargin: GameSettings.fieldMargin + icon.width
            }
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            minimumPixelSize: 5
            font.pixelSize: GameSettings.microFontSize
            fontSizeMode: Text.Fit
            color: page.hasError ? GameSettings.textColor : GameSettings.infoColor
            text: page.hasError ? page.errorMessage : page.infoMessage
        }
    }
}
