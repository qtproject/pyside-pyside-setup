// Copyright (C) 2025 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Page {
    id: page
    enabled: !GalleryConfig.disabled

    ColumnLayout {
        anchors.fill: parent
        spacing: 40

        CheckBox {
            id: orientationCheckBox
            text: qsTr("Vertical")
        }

        Label {
            wrapMode: Label.Wrap
            horizontalAlignment: Qt.AlignHCenter
            text: qsTr("SplitView provides a container that arranges items horizontally "
                     + "or vertically, separated by draggable splitters, allowing users "
                     + "to interactively resize adjacent views within an application.")
            Layout.fillWidth: true
        }

        SplitView {
            orientation: orientationCheckBox.checked ? Qt.Vertical : Qt.Horizontal
            Layout.fillHeight: true
            Layout.fillWidth: true

            Rectangle {
                implicitWidth: 200
                implicitHeight: 100
                color: "lightblue"
                SplitView.maximumWidth: 400

                Label {
                    text: "View 1"
                    anchors.centerIn: parent
                }
            }

            Rectangle {
                id: centerItem
                color: "lightgray"
                SplitView.minimumWidth: 50
                SplitView.minimumHeight: 50
                SplitView.fillWidth: true
                SplitView.fillHeight: true

                Label {
                    text: "View 2"
                    anchors.centerIn: parent
                }
            }

            Rectangle {
                implicitWidth: 200
                implicitHeight: 100
                color: "lightgreen"

                Label {
                    text: "View 3"
                    anchors.centerIn: parent
                }
            }
        }
    }
}
