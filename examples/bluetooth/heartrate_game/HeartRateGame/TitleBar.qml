// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

pragma ComponentBehavior: Bound
import QtQuick

Rectangle {
    id: titleBar

    property var __titles: ["CONNECT", "MEASURE", "STATS"]
    property int currentIndex: 0

    signal titleClicked(int index)

    height: GameSettings.fieldHeight
    color: GameSettings.titleColor

    Rectangle {
        anchors.bottom: parent.bottom
        width: parent.width / 3
        height: parent.height
        x: titleBar.currentIndex * width
        color: GameSettings.selectedTitleColor

        BottomLine {
            color: GameSettings.bottomLineColor
        }

        Behavior on x {
            NumberAnimation {
                duration: 200
            }
        }
    }

    Repeater {
        model: 3
        Rectangle {
            id: caption
            required property int index
            property bool hoveredOrPressed: mouseArea.pressed || mouseArea.containsMouse
            width: titleBar.width / 3
            height: titleBar.height
            x: index * width
            color: (titleBar.currentIndex !== index) && hoveredOrPressed
                   ? GameSettings.hoverTitleColor : "transparent"
            Text {
                anchors.fill: parent
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                text: titleBar.__titles[caption.index]
                font.pixelSize: GameSettings.microFontSize
                color: GameSettings.textColor
            }
            MouseArea {
                id: mouseArea
                anchors.fill: parent
                hoverEnabled: true
                onClicked: titleBar.titleClicked(caption.index)
            }
        }
    }
}
