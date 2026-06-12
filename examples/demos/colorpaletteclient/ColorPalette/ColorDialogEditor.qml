// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs

import QtExampleStyle

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
    property alias currentColor: colordialogButton.buttonColor

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

        Button {
            id: colordialogButton
            Layout.fillWidth: true
            Layout.preferredHeight: 30
            text: qsTr("Change Color")
            textColor: isColorDark(buttonColor) ?
                           UIStyle.textOnDarkBackground :
                           UIStyle.textOnLightBackground

            onClicked: colorDialog.open()

            function isColorDark(color) {
                return (0.2125 * color.r + 0.7154 * color.g + 0.0721 * color.b) < 0.5;
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

                buttonColor: UIStyle.highlightColor
                buttonBorderColor: UIStyle.highlightBorderColor
                textColor: UIStyle.textColor

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
