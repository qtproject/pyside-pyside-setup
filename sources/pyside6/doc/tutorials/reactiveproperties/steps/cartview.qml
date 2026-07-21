// Copyright (C) 2026 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

// A pure display component. It has no logic of its own: Python loads it with
// load_qml_component(), creates it, and pushes the reactive cart's values
// into these three plain properties.
ApplicationWindow {
    property int price: 0
    property int quantity: 0
    property int total: 0

    visible: true
    width: 320
    height: 220
    title: "Reactive Cart (loaded from Python)"

    ColumnLayout {
        anchors.centerIn: parent
        spacing: 12

        Label {
            text: `Total: ${total}`
            font.pixelSize: 24
            Layout.alignment: Qt.AlignHCenter
        }

        Label {
            text: `price = ${price},  quantity = ${quantity}`
            Layout.alignment: Qt.AlignHCenter
        }
    }
}
