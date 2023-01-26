// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import FileSystemModule

ColumnLayout {
    id: colorScheme

    spacing: 20

    // Inline component that customizes TabButton
    component MyTabButton: TabButton {
        id: root

        implicitWidth: 150
        implicitHeight: 30
        padding: 6
        spacing: 6

        contentItem: Text {
            anchors.centerIn: parent
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter

            text: root.text
            font.bold: true
            color: Colors.text
        }

        background: Rectangle {
            anchors.fill: parent
            implicitHeight: 40

            color: root.checked ? Colors.active : Colors.selection
            Rectangle {
                height: 4
                width: parent.width
                color: root.checked ? Colors.color1 : Colors.selection
            }
        }
    }

    Item {
        // Spacer item
        Layout.fillHeight: true
        Layout.fillWidth: true
    }

    Text {
        Layout.alignment: Qt.AlignHCenter

        text: "Select a Scheme!"
        font.pointSize: 30
        font.bold: true
        color: Colors.text
    }

    // Display all the color-scheme names. The model is a string-list provided
    // by our python class.
    TabBar {
        id: schemeSelector

        Layout.alignment: Qt.AlignHCenter

        background: Rectangle {
            color: Colors.surface1
        }

        Repeater {
            model: Colors.getKeys()
            MyTabButton {
                text: modelData
                onClicked: {
                    Colors.setScheme(modelData)
                    themePreviewContainer.background
                            = (modelData === "Solarized") ? "#777777" : "#FEFAEC"
                }
            }
        }
    }

    // The current colors can be visualized using the same method as above.
    Rectangle {
        id: themePreviewContainer

        property color background: "#FEFAEC"

        Layout.alignment: Qt.AlignHCenter

        width: 700
        height: 50
        radius: 10
        color: background

        // Display all used colors inside a row
        Row {
            anchors.centerIn: parent
            spacing: 10

            Repeater {
                model: Colors.currentColors
                Rectangle {
                    width: 35
                    height: width
                    radius: width / 2
                    color: modelData
                }
            }
        }
    }
    Item {
        // Spacer item
        Layout.fillHeight: true
        Layout.fillWidth: true
    }
}
