// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    property alias goButton: goButton
    property alias clearButton: clearButton
    property alias postalCode: postalCode
    property alias street: street
    property alias city: city
    property alias stateName: stateName
    property alias country: country
    property alias cancelButton: cancelButton
    Rectangle {
        id: tabRectangle
        y: 20
        height: tabTitle.height * 2
        color: "#46a2da"
        anchors.rightMargin: 0
        anchors.leftMargin: 0
        anchors.left: parent.left
        anchors.right: parent.right

        Label {
            id: tabTitle
            color: "#ffffff"
            text: qsTr("Geocode")
            anchors.verticalCenter: parent.verticalCenter
            anchors.horizontalCenter: parent.horizontalCenter
        }
    }

    Item {
        id: item2
        anchors.rightMargin: 20
        anchors.leftMargin: 20
        anchors.bottomMargin: 20
        anchors.topMargin: 20
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: tabRectangle.bottom


        GridLayout {
            id: gridLayout3
            anchors.rightMargin: 0
            anchors.bottomMargin: 0
            anchors.leftMargin: 0
            anchors.topMargin: 0
            rowSpacing: 10
            rows: 1
            columns: 2
            anchors.fill: parent

            Label {
                id: label2
                text: qsTr("Street")
            }

            TextField {
                id: street
                Layout.fillWidth: true
            }

            Label {
                id: label3
                text: qsTr("City")
            }

            TextField {
                id: city
                Layout.fillWidth: true
            }

            Label {
                id: label4
                text: qsTr("State")
            }

            TextField {
                id: stateName
                Layout.fillWidth: true
            }

            Label {
                id: label5
                text: qsTr("Country")
            }

            TextField {
                id: country
                Layout.fillWidth: true
            }

            Label {
                id: label6
                text: qsTr("Postal Code")
            }

            TextField {
                id: postalCode
                Layout.fillWidth: true
            }

            RowLayout {
                id: rowLayout1
                Layout.columnSpan: 2
                Layout.alignment: Qt.AlignRight

                Button {
                    id: goButton
                    text: qsTr("Proceed")
                }

                Button {
                    id: clearButton
                    text: qsTr("Clear")
                }

                Button {
                    id: cancelButton
                    text: qsTr("Cancel")
                }
            }

            Item {
                Layout.fillHeight: true
                Layout.columnSpan: 2
            }
        }
    }
}
