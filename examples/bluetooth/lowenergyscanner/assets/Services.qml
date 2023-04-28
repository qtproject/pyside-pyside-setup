// Copyright (C) 2013 BlackBerry Limited. All rights reserved.
// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick

Rectangle {
    width: 300
    height: 600

    Component.onCompleted: {
        // Loading this page may take longer than QLEController
        // stopping with an error, go back and readjust this view
        // based on controller errors
        if (device.controller_error) {
            info.visible = false;
            menu.menuText = device.update
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
        dialogText: "Scanning for services...";
    }

    Connections {
        target: device
        function onservices_updated() {
            if (servicesview.count === 0)
                info.dialogText = "No services found"
            else
                info.visible = false;
        }

        function onDisconnected() {
            pageLoader.source = "qrc:/assets/main.qml"
        }
    }

    ListView {
        id: servicesview
        width: parent.width
        anchors.top: header.bottom
        anchors.bottom: menu.top
        model: device.services_list
        clip: true

        delegate: Rectangle {
            id: servicebox
            height:100
            color: "lightsteelblue"
            border.width: 2
            border.color: "black"
            radius: 5
            width: servicesview.width
            Component.onCompleted: {
                info.visible = false
            }

            MouseArea {
                anchors.fill: parent
                onClicked: {
                    pageLoader.source = "qrc:/assets/Characteristics.qml";
                    device.connect_to_service(modelData.service_uuid);
                }
            }

            Label {
                id: service_name
                textContent: modelData.service_name
                anchors.top: parent.top
                anchors.topMargin: 5
            }

            Label {
                textContent: modelData.service_type
                font.pointSize: service_name.font.pointSize * 0.5
                anchors.top: service_name.bottom
            }

            Label {
                id: service_uuid
                font.pointSize: service_name.font.pointSize * 0.5
                textContent: modelData.service_uuid
                anchors.bottom: servicebox.bottom
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
            device.disconnect_from_device()
            pageLoader.source = "qrc:/assets/main.qml"
            device.update = "Search"
        }
    }
}
