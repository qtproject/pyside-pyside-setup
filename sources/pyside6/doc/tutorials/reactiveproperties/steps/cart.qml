// Copyright (C) 2026 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Shop

ApplicationWindow {
    visible: true
    width: 320
    height: 220
    title: "Reactive Cart"

    Cart { id: cart }

    ColumnLayout {
        anchors.centerIn: parent
        spacing: 12

        // Reads the @computed 'total'. It re-evaluates automatically whenever
        // price or quantity changes, because each fires its notify signal.
        Label {
            text: `Total: ${cart.total}`
            font.pixelSize: 24
            Layout.alignment: Qt.AlignHCenter
        }

        RowLayout {
            Label { text: "Price:" }
            // Writing cart.price runs the generated setter, which fires the
            // @watch and @effect callbacks and invalidates 'total'.
            SpinBox {
                from: 1
                to: 999
                value: cart.price
                onValueModified: cart.price = value
            }
        }

        RowLayout {
            Label { text: "Quantity:" }
            SpinBox {
                from: 1
                to: 99
                value: cart.quantity
                onValueModified: cart.quantity = value
            }
        }
    }
}
