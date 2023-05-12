// Copyright (C) 2013 BlackBerry Limited. All rights reserved.
// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick

Rectangle {
    id: menu

    property real menuWidth: 100
    property real menuHeight: 50
    property string menuText: "Search"
    signal buttonClick

    height: menuHeight
    width: menuWidth

    Rectangle {
        id: search
        width: parent.width
        height: parent.height
        anchors.centerIn: parent
        color: "#363636"
        border.width: 1
        border.color: "#E3E3E3"
        radius: 5
        Text {
            id: searchText
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            anchors.fill: parent
            text: menu.menuText
            elide: Text.ElideMiddle
            color: "#E3E3E3"
            wrapMode: Text.WordWrap
        }

        MouseArea {
            anchors.fill: parent
            onPressed: {
                search.width = search.width - 7
                search.height = search.height - 5
            }

            onReleased: {
                search.width = search.width + 7
                search.height = search.height + 5
            }

            onClicked: {
                menu.buttonClick()
            }
        }
    }
}
