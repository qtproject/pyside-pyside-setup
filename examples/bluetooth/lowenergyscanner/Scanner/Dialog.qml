// Copyright (C) 2013 BlackBerry Limited. All rights reserved.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick

Rectangle {
    id: dialog
    width: parent.width / 3 * 2
    height: dialogTextId.height + background.height + 20
    z: 50
    property string dialogText: ""
    property bool busyImage: true
    border.width: 1
    border.color: "#363636"
    radius: 10

    Text {
        id: dialogTextId
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.top
        anchors.topMargin: 10

        elide: Text.ElideMiddle
        text: dialog.dialogText
        color: "#363636"
        wrapMode: Text.Wrap
    }

    Image {
        id: background

        width: 20
        height: 20
        anchors.top: dialogTextId.bottom
        anchors.horizontalCenter: dialogTextId.horizontalCenter
        visible: parent.busyImage
        source: "assets/busy_dark.png"
        fillMode: Image.PreserveAspectFit
        NumberAnimation on rotation {
            duration: 3000
            from: 0
            to: 360
            loops: Animation.Infinite
        }
    }
}
