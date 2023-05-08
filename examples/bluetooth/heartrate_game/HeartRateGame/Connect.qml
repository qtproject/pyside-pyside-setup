// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

pragma ComponentBehavior: Bound
import QtQuick
import HeartRateGame

GamePage {
    id: connectPage

    required property ConnectionHandler connectionHandler
    required property DeviceFinder deviceFinder
    required property DeviceHandler deviceHandler

    signal showMeasurePage

    errorMessage: deviceFinder.error
    infoMessage: deviceFinder.info

    Rectangle {
        id: viewContainer
        anchors.top: parent.top
        // only BlueZ platform has address type selection
        anchors.bottom: connectPage.connectionHandler.requiresAddressType ? addressTypeButton.top
                                                                          : searchButton.top
        anchors.topMargin: GameSettings.fieldMargin + connectPage.messageHeight
        anchors.bottomMargin: GameSettings.fieldMargin
        anchors.horizontalCenter: parent.horizontalCenter
        width: parent.width - GameSettings.fieldMargin * 2
        color: GameSettings.viewColor
        radius: GameSettings.buttonRadius

        Text {
            id: title
            width: parent.width
            height: GameSettings.fieldHeight
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            color: GameSettings.textColor
            font.pixelSize: GameSettings.mediumFontSize
            text: qsTr("FOUND DEVICES")

            BottomLine {
                height: 1
                width: parent.width
                color: "#898989"
            }
        }

        ListView {
            id: devices
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            anchors.top: title.bottom
            model: connectPage.deviceFinder.devices
            clip: true

            delegate: Rectangle {
                id: box

                required property int index
                required property var modelData

                height: GameSettings.fieldHeight * 1.2
                width: devices.width
                color: index % 2 === 0 ? GameSettings.delegate1Color : GameSettings.delegate2Color

                MouseArea {
                    anchors.fill: parent
                    onClicked: {
                        connectPage.deviceFinder.connectToService(box.modelData.deviceAddress)
                        connectPage.showMeasurePage()
                    }
                }

                Text {
                    id: device
                    font.pixelSize: GameSettings.smallFontSize
                    text: box.modelData.deviceName
                    anchors.top: parent.top
                    anchors.topMargin: parent.height * 0.1
                    anchors.leftMargin: parent.height * 0.1
                    anchors.left: parent.left
                    color: GameSettings.textColor
                }

                Text {
                    id: deviceAddress
                    font.pixelSize: GameSettings.smallFontSize
                    text: box.modelData.deviceAddress
                    anchors.bottom: parent.bottom
                    anchors.bottomMargin: parent.height * 0.1
                    anchors.rightMargin: parent.height * 0.1
                    anchors.right: parent.right
                    color: Qt.darker(GameSettings.textColor)
                }
            }
        }
    }

    GameButton {
        id: addressTypeButton
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: searchButton.top
        anchors.bottomMargin: GameSettings.fieldMargin * 0.5
        width: viewContainer.width
        height: GameSettings.fieldHeight
        visible: connectPage.connectionHandler.requiresAddressType // only required on BlueZ
        state: "public"
        onClicked: state === "public" ? state = "random" : state = "public"

        states: [
            State {
                name: "public"
                PropertyChanges {
                    addressTypeText.text: qsTr("Public Address")
                }
                PropertyChanges {
                    connectPage.deviceHandler.addressType: DeviceHandler.PUBLIC_ADDRESS
                }
            },
            State {
                name: "random"
                PropertyChanges {
                    addressTypeText.text: qsTr("Random Address")
                }
                PropertyChanges {
                    connectPage.deviceHandler.addressType: DeviceHandler.RANDOM_ADDRESS
                }
            }
        ]

        Text {
            id: addressTypeText
            anchors.centerIn: parent
            font.pixelSize: GameSettings.tinyFontSize
            color: GameSettings.textColor
        }
    }

    GameButton {
        id: searchButton
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: GameSettings.fieldMargin
        width: viewContainer.width
        height: GameSettings.fieldHeight
        enabled: !connectPage.deviceFinder.scanning
        onClicked: connectPage.deviceFinder.startSearch()

        Text {
            anchors.centerIn: parent
            font.pixelSize: GameSettings.tinyFontSize
            text: qsTr("START SEARCH")
            color: searchButton.enabled ? GameSettings.textColor : GameSettings.disabledTextColor
        }
    }
}
