// Copyright (C) 2013 BlackBerry Limited. All rights reserved.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick

Rectangle {
    id: header
    width: parent.width
    height: 70
    border.width: 1
    border.color: "#363636"
    radius: 5
    property string headerText: ""

    Text {
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        anchors.fill: parent
        text: header.headerText
        font.bold: true
        font.pointSize: 20
        elide: Text.ElideMiddle
        color: "#363636"
    }
}
