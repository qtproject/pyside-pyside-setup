// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick
import QtQuick.Controls

Menu {
    property variant type
    signal itemClicked(string item)

    MenuItem {
        text: qsTr("Info")
        onTriggered: itemClicked("show" + type + "Info")
    }
    MenuItem {
        text: qsTr("Delete")
        onTriggered: itemClicked("delete" + type)
    }
}
