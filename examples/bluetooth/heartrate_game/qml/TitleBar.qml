// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick

Rectangle    {
    id: titleBar
    anchors.top: parent.top
    anchors.left: parent.left
    anchors.right: parent.right
    height: GameSettings.fieldHeight
    color: GameSettings.viewColor

    property var __titles: ["CONNECT", "MEASURE", "STATS"]
    property int currentIndex: 0

    signal titleClicked(int index)

    Repeater {
        model: 3
        Text {
            width: titleBar.width / 3
            height: titleBar.height
            x: index * width
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            text: __titles[index]
            font.pixelSize: GameSettings.tinyFontSize
            color: titleBar.currentIndex === index ? GameSettings.textColor : GameSettings.disabledTextColor

            MouseArea {
                anchors.fill: parent
                onClicked: titleClicked(index)
            }
        }
    }


    Item {
        anchors.bottom: parent.bottom
        width: parent.width / 3
        height: parent.height
        x: currentIndex * width

        BottomLine{}

        Behavior on x { NumberAnimation { duration: 200 } }
    }

}
