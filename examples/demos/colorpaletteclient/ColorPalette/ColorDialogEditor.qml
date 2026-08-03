// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs

Popup {
    id: colorEditor
    // Popup for adding or updating a color
    padding: 10
    modal: true
    focus: true
    anchors.centerIn: parent
    closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutsideParent
    signal colorAdded(string name, string color, string pantone_value)
    signal colorUpdated(string name, string color, string pantone_value, int cid)

    property bool newColor: true
    property int colorId: -1
    property color currentColor: "white"

    function createNewColor() {
        newColor = true
        colorNameField.text = "cute green"
        currentColor = Qt.color("#41cd52")
        colorPantoneField.text = "PMS 802C"
        colorDialog.selectedColor = currentColor
        open()
    }

    function updateColor(data) {
        newColor = false
        colorNameField.text = data.name
        currentColor = Qt.color(data.color)
        colorPantoneField.text = data.pantone_value
        colorId = data.id
        colorDialog.selectedColor = currentColor
        open()
    }

    ColorDialog {
        id: colorDialog
        title: qsTr("Choose a color")
        onAccepted: {
            colorEditor.currentColor = Qt.color(colorDialog.selectedColor)
            colorDialog.close()
        }
        onRejected: {
            colorDialog.close()
        }
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 10

        GridLayout {
            columns: 2
            rowSpacing: 10
            columnSpacing: 10

            Label {
                text: qsTr("Color Name")
            }
            TextField {
                id: colorNameField
                padding: 10
            }

            Label {
                text: qsTr("Pantone Value")
            }
            TextField {
                id: colorPantoneField
                padding: 10
            }

            Label {
                text: qsTr("Rgb Value")
            }

            TextField {
                id: colorRGBField
                text: colorEditor.currentColor.toString()
                readOnly: true
                padding: 10
            }
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 10

            Rectangle {
                Layout.preferredWidth: 30
                Layout.preferredHeight: 30
                Layout.minimumWidth: 30
                Layout.minimumHeight: 30
                radius: 4
                border.width: 1
                border.color: palette.mid
                color: colorEditor.currentColor
            }

            Button {
                Layout.fillWidth: true
                text: qsTr("Change Color")
                onClicked: colorDialog.open()
            }
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 10

            Button {
                text: qsTr("Cancel")
                onClicked: colorEditor.close()
                Layout.fillWidth: true
            }

            Button {
                Layout.fillWidth: true
                text: colorEditor.newColor ? qsTr("Add") : qsTr("Update")

                onClicked: {
                    if (colorEditor.newColor) {
                        colorEditor.colorAdded(colorNameField.text,
                                               colorRGBField.text,
                                               colorPantoneField.text)
                    } else {
                        colorEditor.colorUpdated(colorNameField.text,
                                                 colorRGBField.text,
                                                 colorPantoneField.text,
                                                 colorEditor.colorId)
                    }
                    colorEditor.close()
                }
            }
        }
    }
}
