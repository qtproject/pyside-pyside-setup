// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause


import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import QtQuick.Window
import QtQuick.Controls.Material

import io.qt.textproperties

ApplicationWindow {
    id: page
    width: 800
    height: 400
    visible: true
    Material.theme: Material.Dark
    Material.accent: Material.Red

    Bridge {
        id: bridge
    }

    GridLayout {
        id: grid
        columns: 2
        rows: 3

        ColumnLayout {
            spacing: 2
            Layout.columnSpan: 1
            Layout.preferredWidth: 400

            Text {
                id: leftlabel
                Layout.alignment: Qt.AlignHCenter
                color: "white"
                font.pointSize: 16
                text: "Qt for Python"
                Layout.preferredHeight: 100
                Material.accent: Material.Green
            }

            RadioButton {
                id: italic
                Layout.alignment: Qt.AlignLeft
                text: "Italic"
                onToggled: {
                    leftlabel.font.italic = bridge.getItalic(italic.text)
                    leftlabel.font.bold = bridge.getBold(italic.text)
                    leftlabel.font.underline = bridge.getUnderline(italic.text)

                }
            }
            RadioButton {
                id: bold
                Layout.alignment: Qt.AlignLeft
                text: "Bold"
                onToggled: {
                    leftlabel.font.italic = bridge.getItalic(bold.text)
                    leftlabel.font.bold = bridge.getBold(bold.text)
                    leftlabel.font.underline = bridge.getUnderline(bold.text)
                }
            }
            RadioButton {
                id: underline
                Layout.alignment: Qt.AlignLeft
                text: "Underline"
                onToggled: {
                    leftlabel.font.italic = bridge.getItalic(underline.text)
                    leftlabel.font.bold = bridge.getBold(underline.text)
                    leftlabel.font.underline = bridge.getUnderline(underline.text)
                }
            }
            RadioButton {
                id: noneradio
                Layout.alignment: Qt.AlignLeft
                text: "None"
                checked: true
                onToggled: {
                    leftlabel.font.italic = bridge.getItalic(noneradio.text)
                    leftlabel.font.bold = bridge.getBold(noneradio.text)
                    leftlabel.font.underline = bridge.getUnderline(noneradio.text)
                }
            }
        }

        ColumnLayout {
            id: rightcolumn
            spacing: 2
            Layout.columnSpan: 1
            Layout.preferredWidth: 400
            Layout.preferredHeight: 400
            Layout.fillWidth: true

            RowLayout {
                Layout.alignment: Qt.AlignVCenter | Qt.AlignHCenter


                Button {
                    id: red
                    text: "Red"
                    highlighted: true
                    Material.accent: Material.Red
                    onClicked: {
                        leftlabel.color = bridge.getColor(red.text)
                    }
                }
                Button {
                    id: green
                    text: "Green"
                    highlighted: true
                    Material.accent: Material.Green
                    onClicked: {
                        leftlabel.color = bridge.getColor(green.text)
                    }
                }
                Button {
                    id: blue
                    text: "Blue"
                    highlighted: true
                    Material.accent: Material.Blue
                    onClicked: {
                        leftlabel.color = bridge.getColor(blue.text)
                    }
                }
                Button {
                    id: nonebutton
                    text: "None"
                    highlighted: true
                    Material.accent: Material.BlueGrey
                    onClicked: {
                        leftlabel.color = bridge.getColor(nonebutton.text)
                    }
                }
            }
            RowLayout {
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignVCenter | Qt.AlignHCenter
                Text {
                    id: rightlabel
                    color: "white"
                    Layout.alignment: Qt.AlignLeft
                    text: "Font size"
                    Material.accent: Material.White
                }
                Slider {
                    width: rightcolumn.width*0.6
                    Layout.alignment: Qt.AlignRight
                    id: slider
                    value: 0.5
                    onValueChanged: {
                        leftlabel.font.pointSize = bridge.getSize(value)
                    }
                }
            }
        }
    }
}
