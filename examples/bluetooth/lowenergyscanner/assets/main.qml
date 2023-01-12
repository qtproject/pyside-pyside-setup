// Copyright (C) 2013 BlackBerry Limited. All rights reserved.
// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick

Rectangle {
    id: back
    width: 300
    height: 600
    property bool deviceState: device.state
    onDevicestate_changed: {
        if (!device.state)
            info.visible = false;
    }

    Header {
        id: header
        anchors.top: parent.top
        headerText: "Start Discovery"
    }

    Dialog {
        id: info
        anchors.centerIn: parent
        visible: false
    }

    ListView {
        id: theListView
        width: parent.width
        clip: true

        anchors.top: header.bottom
        anchors.bottom: connectToggle.top
        model: device.devices_list

        delegate: Rectangle {
            id: box
            height:100
            width: theListView.width
            color: "lightsteelblue"
            border.width: 2
            border.color: "black"
            radius: 5

            Component.onCompleted: {
                info.visible = false;
                header.headerText = "Select a device";
            }

            MouseArea {
                anchors.fill: parent
                onClicked: {
                    device.scan_services(modelData.device_address);
                    pageLoader.source = "qrc:/assets/Services.qml"
                }
            }

            Label {
                id: device_name
                textContent: modelData.device_name
                anchors.top: parent.top
                anchors.topMargin: 5
            }

            Label {
                id: device_address
                textContent: modelData.device_address
                font.pointSize: device_name.font.pointSize*0.7
                anchors.bottom: box.bottom
                anchors.bottomMargin: 5
            }
        }
    }

    Menu {
        id: connectToggle

        menuWidth: parent.width
        anchors.bottom: menu.top
        menuText: { if (device.devices_list.length)
                        visible = true
                    else
                        visible = false
                    if (device.use_random_address)
                        "Address type: Random"
                    else
                        "Address type: Public"
        }

        onButtonClick: device.use_random_address = !device.use_random_address;
    }

    Menu {
        id: menu
        anchors.bottom: parent.bottom
        menuWidth: parent.width
        menuHeight: (parent.height/6)
        menuText: device.update
        onButtonClick: {
            device.start_device_discovery();
            // if start_device_discovery() failed device.state is not set
            if (device.state) {
                info.dialogText = "Searching...";
                info.visible = true;
            }
        }
    }

    Loader {
        id: pageLoader
        anchors.fill: parent
    }
}
