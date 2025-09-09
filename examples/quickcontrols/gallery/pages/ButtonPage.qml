// Copyright (C) 2017 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick
import QtQuick.Layouts
import QtQuick.Controls

ScrollablePage {
    id: page

    Column {
        spacing: 40
        width: parent.width

        Row {
            CheckBox {
                id: checkedCheckBox
                text: qsTr("Checked")
            }

            CheckBox {
                id: flatCheckBox
                text: qsTr("Flat")
            }

            CheckBox {
                id: pressedCheckBox
                enabled: !GalleryConfig.disabled
                text: qsTr("Pressed")
            }
        }

        Label {
            width: parent.width
            wrapMode: Label.Wrap
            horizontalAlignment: Qt.AlignHCenter
            text: qsTr("Button presents a push-button that can be pushed or clicked by the user. "
                + "Buttons are normally used to perform an action, or to answer a question.")
        }

        ColumnLayout {
            spacing: 20
            anchors.horizontalCenter: parent.horizontalCenter

            Button {
                enabled: !GalleryConfig.disabled
                text: qsTr("Button")
                checked: checkedCheckBox.checked
                flat: flatCheckBox.checked
                down: pressedCheckBox.checked ? true : undefined
                Layout.fillWidth: true
            }
            Button {
                enabled: !GalleryConfig.disabled
                text: qsTr("Highlighted")
                checked: checkedCheckBox.checked
                flat: flatCheckBox.checked
                down: pressedCheckBox.checked ? true : undefined
                highlighted: true
                Layout.fillWidth: true
            }
            RoundButton {
                enabled: !GalleryConfig.disabled
                text: qsTr("RoundButton")
                checked: checkedCheckBox.checked
                flat: flatCheckBox.checked
                down: pressedCheckBox.checked ? true : undefined
                Layout.fillWidth: true
            }
        }
    }
}
