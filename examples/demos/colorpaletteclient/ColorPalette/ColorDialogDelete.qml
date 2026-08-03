// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Popup {
    id: colorDeleter
    padding: 10
    modal: true
    focus: true
    anchors.centerIn: parent
    closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutsideParent
    signal deleteClicked(int cid)

    property int colorId: -1

    property string colorName: ""

    function maybeDelete(data) {
        colorName = data.name
        colorId = data.id
        open()
    }


    ColumnLayout {
        anchors.fill: parent
        spacing: 10

        Label {
            text: qsTr("Delete Color?")
            font.bold: true
        }

        Label {
            text: qsTr("Are you sure, you want to delete color") + " \"" + colorDeleter.colorName + "\"?"
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 10

            Button {
                Layout.fillWidth: true
                text: qsTr("Cancel")
                onClicked: colorDeleter.close()
            }

            Button {
                Layout.fillWidth: true
                text: qsTr("Delete")

                onClicked: {
                    colorDeleter.deleteClicked(colorDeleter.colorId)
                    colorDeleter.close()
                }
            }
       }
    }
}
