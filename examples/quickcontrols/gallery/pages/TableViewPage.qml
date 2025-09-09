// Copyright (C) 2025 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Qt.labs.qmlmodels

Page {
    id: page
    enabled: !GalleryConfig.disabled

    GridLayout {
        anchors.fill: parent

        Label {
            wrapMode: Label.Wrap
            horizontalAlignment: Qt.AlignHCenter
            text: qsTr("TableView provides a scrollable grid that displays data from "
                       + "a model in rows and columns, allowing users to view and interact "
                       + "with structured information within an application.")
            Layout.fillWidth: true
            Layout.columnSpan: 2
        }

        HorizontalHeaderView {
            clip: true
            syncView: tableView
            model: tableModel.headerModel
            Layout.column: 1
            Layout.row: 1
            Layout.fillWidth: true
        }

        VerticalHeaderView {
            clip: true
            syncView: tableView
            Layout.column: 0
            Layout.row: 2
            Layout.fillHeight: true
        }

        TableView {
            id: tableView
            columnSpacing: 1
            rowSpacing: 1
            clip: true

            selectionModel: ItemSelectionModel {}
            model: tableModel

            Layout.column: 1
            Layout.row: 2
            Layout.fillWidth: true
            Layout.fillHeight: true

            delegate: TableViewDelegate {
                implicitWidth: 100
                implicitHeight: 50
                Component.onCompleted: {
                    if (contentItem as Label) {
                        contentItem.horizontalAlignment = Qt.AlignHCenter
                        contentItem.verticalAlignment = Qt.AlignVCenter
                    }
                }
            }
        }
    }

    TableModel {
        id: tableModel
        property var headerModel: [qsTr("Name"), qsTr("Color")]
        TableModelColumn { display: "name" }
        TableModelColumn { display: "color" }
        rows: [
            {
                "name": qsTr("cat"),
                "color": qsTr("black")
            },
            {
                "name": qsTr("dog"),
                "color": qsTr("brown")
            },
            {
                "name": qsTr("bird"),
                "color": qsTr("white")
            }
        ]
    }
}
