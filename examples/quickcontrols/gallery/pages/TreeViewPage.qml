// Copyright (C) 2025 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Qt.labs.qmlmodels

Page {
    id: page

    GridLayout {
        anchors.fill: parent
        anchors.margins: 10

        Label {
            wrapMode: Label.Wrap
            horizontalAlignment: Qt.AlignHCenter
            text: qsTr("TreeView provides a hierarchical view for displaying and "
                     + "navigating tree-structured data, allowing users to expand and "
                     + "collapse nodes to explore parent-child relationships within a model")

            Layout.fillWidth: true
            Layout.columnSpan: 2
        }

        Item {
            implicitHeight: 40

            Layout.columnSpan: 2
            Layout.row: 1
        }

        HorizontalHeaderView {
            clip: true
            enabled: !GalleryConfig.disabled
            syncView: treeView
            model: [qsTr("Location")]

            Layout.column: 1
            Layout.row: 2
            Layout.fillWidth: true
        }

        VerticalHeaderView {
            clip: true
            enabled: !GalleryConfig.disabled
            syncView: treeView
            model: Array.from({length: treeView.rows}, (v, k) => k + 1)

            Layout.column: 0
            Layout.row: 3
            Layout.fillHeight: true
        }

        TreeView {
            id: treeView
            clip: true
            enabled: !GalleryConfig.disabled
            rowSpacing: 2
            model: treeModel

            Layout.column: 1
            Layout.row: 3
            Layout.fillWidth: true
            Layout.fillHeight: true

            selectionModel: ItemSelectionModel {}
            delegate: TreeViewDelegate { }

            columnWidthProvider: (column) => column === 0 ? treeView.width : 0

            Component.onCompleted: expandRecursively()
        }
    }

    TreeModel {
        id: treeModel

        TableModelColumn { display: "location" }

        rows: [
            {
                location: qsTr("America"),
                rows: [
                    { location: qsTr("Brazil") },
                    {
                        location: qsTr("Canada"),
                        rows: [
                            { location: qsTr("Calgary") },
                            { location: qsTr("Vancouver") }
                        ]
                    }
                ]
            },
            { location: qsTr("Asia") },
            {
                location: qsTr("Europe"),
                rows: [
                    {
                        location: qsTr("Italy"),
                        rows: [
                            { location: qsTr("Milan") },
                            { location: qsTr("Rome") }
                        ]
                    },
                    { location: qsTr("Portugal") }
                ]
            }

        ]
    }
}
