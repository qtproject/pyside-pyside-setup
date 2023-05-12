// Copyright (C) 2013 BlackBerry Limited. All rights reserved.
// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

pragma ComponentBehavior: Bound
import QtQuick

Rectangle {
    id: characteristicsPage

    signal showServices
    signal showDevices

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
        dialogText: "Scanning for characteristics..."
    }

    Connections {
        target: Device
        function oncharacteristics_pdated() {
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
            characteristicsPage.showDevices()
        }
    }

    ListView {
        id: characteristicview
        width: parent.width
        clip: true

        anchors.top: header.bottom
        anchors.bottom: menu.top
        model: Device.characteristicList

        delegate: Rectangle {
            required property var modelData
            id: box
            height: 300
            width: characteristicview.width
            color: "lightsteelblue"
            border.width: 2
            border.color: "black"
            radius: 5

            Label {
                id: characteristicName
                textContent: box.modelData.characteristic_name
                anchors.top: parent.top
                anchors.topMargin: 5
            }

            Label {
                id: characteristicUuid
                font.pointSize: characteristicName.font.pointSize * 0.7
                textContent: box.modelData.characteristic_uuid
                anchors.top: characteristicName.bottom
                anchors.topMargin: 5
            }

            Label {
                id: characteristicValue
                font.pointSize: characteristicName.font.pointSize * 0.7
                textContent: ("Value: " + box.modelData.characteristic_value)
                anchors.bottom: characteristicHandle.top
                horizontalAlignment: Text.AlignHCenter
                anchors.topMargin: 5
            }

            Label {
                id: characteristicHandle
                font.pointSize: characteristicName.font.pointSize * 0.7
                textContent: ("Handlers: " + box.modelData.characteristic_handle)
                anchors.bottom: characteristicPermission.top
                anchors.topMargin: 5
            }

            Label {
                id: characteristicPermission
                font.pointSize: characteristicName.font.pointSize * 0.7
                textContent: box.modelData.characteristic_permission
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
        menuText: Device.update
        menuHeight: (parent.height / 6)
        onButtonClick: {
            characteristicsPage.showServices()
            Device.update = "Back"
        }
    }
}
