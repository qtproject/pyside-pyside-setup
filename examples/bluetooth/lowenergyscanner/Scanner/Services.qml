// Copyright (C) 2013 BlackBerry Limited. All rights reserved.
// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

pragma ComponentBehavior: Bound
import QtQuick

Rectangle {
    id: servicesPage

    signal showCharacteristics
    signal showDevices

    width: 300
    height: 600

    Component.onCompleted: {
        // Loading this page may take longer than QLEController
        // stopping with an error, go back and readjust this view
        // based on controller errors
        if (Device.controller_error) {
            info.visible = false
            menu.menuText = Device.update
        }
    }

    Header {
        id: header
        anchors.top: parent.top
        headerText: "Services list"
    }

    Dialog {
        id: info
        anchors.centerIn: parent
        visible: true
        dialogText: "Scanning for services..."
    }

    Connections {
        target: Device
        function onservices_updated() {
            if (servicesview.count === 0)
                info.dialogText = "No services found"
            else
                info.visible = false
        }

        function ondisconnected() {
            servicesPage.showDevices()
        }
    }

    ListView {
        id: servicesview
        width: parent.width
        anchors.top: header.bottom
        anchors.bottom: menu.top
        model: Device.servicesList
        clip: true

        delegate: Rectangle {
            required property var modelData
            id: box
            height: 100
            color: "lightsteelblue"
            border.width: 2
            border.color: "black"
            radius: 5
            width: servicesview.width

            MouseArea {
                anchors.fill: parent
                onClicked: {
                    Device.connectToService(box.modelData.service_uuid)
                    servicesPage.showCharacteristics()
                }
            }

            Label {
                id: serviceName
                textContent: box.modelData.service_name
                anchors.top: parent.top
                anchors.topMargin: 5
            }

            Label {
                textContent: box.modelData.service_type
                font.pointSize: serviceName.font.pointSize * 0.5
                anchors.top: serviceName.bottom
            }

            Label {
                id: serviceUuid
                font.pointSize: serviceName.font.pointSize * 0.5
                textContent: box.modelData.service_uuid
                anchors.bottom: box.bottom
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
            Device.disconnect_from_device()
            servicesPage.showDevices()
            Device.update = "Search"
        }
    }
}
