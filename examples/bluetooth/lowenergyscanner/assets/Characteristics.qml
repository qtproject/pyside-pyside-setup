// Copyright (C) 2013 BlackBerry Limited. All rights reserved.
// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick

Rectangle {
    width: 300
    height: 600

    Header {
        id: header
        anchors.top: parent.top
        headerText: "Characteristics list"
    }

    Dialog {
        id: info
        anchors.centerIn: parent
        visible: true
        dialogText: "Scanning for characteristics...";
    }

    Connections {
        target: device
        function oncharacteristic_updated() {
            menu.menuText = "Back"
            if (characteristicview.count === 0) {
                info.dialogText = "No characteristic found"
                info.busyImage = false
            } else {
                info.visible = false
                info.busyImage = true
            }
        }

        function onDisconnected() {
            pageLoader.source = "qrc:/assets/main.qml"
        }
    }

    ListView {
        id: characteristicview
        width: parent.width
        clip: true

        anchors.top: header.bottom
        anchors.bottom: menu.top
        model: device.characteristic_list

        delegate: Rectangle {
            id: characteristicbox
            height:300
            width: characteristicview.width
            color: "lightsteelblue"
            border.width: 2
            border.color: "black"
            radius: 5

            Label {
                id: characteristic_name
                textContent: modelData.characteristic_name
                anchors.top: parent.top
                anchors.topMargin: 5
            }

            Label {
                id: characteristic_uuid
                font.pointSize: characteristic_name.font.pointSize*0.7
                textContent: modelData.characteristic_uuid
                anchors.top: characteristic_name.bottom
                anchors.topMargin: 5
            }

            Label {
                id: characteristic_value
                font.pointSize: characteristic_name.font.pointSize*0.7
                textContent: ("Value: " + modelData.characteristic_value)
                anchors.bottom: characteristicHandle.top
                horizontalAlignment: Text.AlignHCenter
                anchors.topMargin: 5
            }

            Label {
                id: characteristicHandle
                font.pointSize: characteristic_name.font.pointSize*0.7
                textContent: ("Handlers: " + modelData.characteristicHandle)
                anchors.bottom: characteristic_permission.top
                anchors.topMargin: 5
            }

            Label {
                id: characteristic_permission
                font.pointSize: characteristic_name.font.pointSize*0.7
                textContent: modelData.characteristic_permission
                anchors.bottom: parent.bottom
                anchors.topMargin: 5
                anchors.bottomMargin: 5
            }
        }
    }

    Menu {
        id: menu
        anchors.bottom: parent.bottom
        menuWidth: parent.width
        menuText: device.update
        menuHeight: (parent.height/6)
        onButtonClick: {
            pageLoader.source = "qrc:/assets/Services.qml"
            device.update = "Back"
        }
    }
}
