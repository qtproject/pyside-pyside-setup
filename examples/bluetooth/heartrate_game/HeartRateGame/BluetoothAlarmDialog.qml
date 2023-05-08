// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick

Item {
    id: root

    property bool permissionError: false

    anchors.fill: parent

    Rectangle {
        anchors.fill: parent
        color: "black"
        opacity: 0.9
    }

    MouseArea {
        id: eventEater
    }

    Rectangle {
        id: dialogFrame

        anchors.centerIn: parent
        width: parent.width * 0.8
        height: parent.height * 0.6
        border.color: "#454545"
        color: GameSettings.backgroundColor
        radius: width * 0.05

        Item {
            id: dialogContainer
            anchors.fill: parent
            anchors.margins: parent.width*0.05

            Image {
                id: offOnImage
                anchors.left: quitButton.left
                anchors.right: quitButton.right
                anchors.top: parent.top
                height: GameSettings.heightForWidth(width, sourceSize)
                source: "images/bt_off_to_on.png"
            }

            Text {
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: offOnImage.bottom
                anchors.bottom: quitButton.top
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                wrapMode: Text.WordWrap
                font.pixelSize: GameSettings.mediumFontSize
                color: GameSettings.textColor
                text: root.permissionError
                      ? qsTr("Bluetooth permissions are not granted. Please grant the permissions in the system settings.")
                      : qsTr("This application cannot be used without Bluetooth. Please switch Bluetooth ON to continue.")
            }

            GameButton {
                id: quitButton
                anchors.bottom: parent.bottom
                anchors.horizontalCenter: parent.horizontalCenter
                width: dialogContainer.width * 0.6
                height: GameSettings.buttonHeight
                onClicked: Qt.quit()

                Text {
                    anchors.centerIn: parent
                    color: GameSettings.textColor
                    font.pixelSize: GameSettings.bigFontSize
                    text: qsTr("Quit")
                }
            }
        }
    }
}
