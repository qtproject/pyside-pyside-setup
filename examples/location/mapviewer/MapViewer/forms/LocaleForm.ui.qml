// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    property alias clearButton: clearButton
    property alias goButton: goButton
    property alias cancelButton: cancelButton
    property alias tabTitle: tabTitle
    property alias languageGroup: languageGroup
    property alias enRadioButton: enRadioButton
    property alias frRadioButton: frRadioButton
    property alias otherRadioButton: otherRadioButton
    property alias language: language

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
            text: "Locale"
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

            ButtonGroup { id: languageGroup }
            RadioButton {
                id: enRadioButton
                text: qsTr("en")
                ButtonGroup.group: languageGroup
                Layout.columnSpan: 2
            }

            RadioButton {
                id: frRadioButton
                text: qsTr("fr")
                ButtonGroup.group: languageGroup
                Layout.columnSpan: 2
            }

            RadioButton {
                id: otherRadioButton
                text: qsTr("Other")
                ButtonGroup.group: languageGroup
            }

            TextField {
                id: language
                Layout.fillWidth: true
                placeholderText: qsTr("")
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
