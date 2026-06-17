// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick
import QtQuick.Controls

ListView {
    id: listview
    width: 200; height: 320
    required model
    ScrollBar.vertical: ScrollBar { }

    delegate: Rectangle {
        id: row
        width: listview.width; height: 25

        required property string name
        required property var modelData

        // Explicit binding so the Rectangle tracks modelData.colorChanged
        // directly. A plain Python list of QObjects never emits dataChanged()
        // This would have not been needed if 'dataList' was done through
        // a QAbstractListModel subclass, which emits dataChanged() on every
        // role update.
        color: modelData.color

        Text { text: parent.name }

        // Click a row to recolor it. Writing modelData.color from QML runs
        // the DataObject's @watch("color") callback on the Python side, and
        // emits colorChanged so this binding refreshes.
        TapHandler {
            onTapped: {
                const palette = ["red", "green", "blue", "yellow", "magenta"]
                const next = (palette.indexOf(row.modelData.color) + 1) % palette.length
                row.modelData.color = palette[next]
            }
        }
    }
}
