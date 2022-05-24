// Copyright (C) 2017 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import QtQuick 2.0

Item {
    id: root
    width: 600
    height: 600

    Rectangle {
        id: blue
        objectName: "blueRectangle"
        width: 200
        height: 200
        anchors.top: root.top
        anchors.horizontalCenter: root.horizontalCenter
        color: "blue"
    }

    Text {
        text: qsTr("Original blue rectangle")
        anchors.left: blue.right
        anchors.verticalCenter: blue.verticalCenter
    }

    Image {
        id: imageContainer
        objectName: "imageContainer"
        width: 200
        height: 200
        anchors.bottom: root.bottom
        anchors.horizontalCenter: root.horizontalCenter
    }

    Text {
        text: qsTr("Image with the source URL set to the result of calling QQuickItem::grabToImage on the rectangle. If you see a second blue rectangle, that means it works.")
        anchors.left: imageContainer.right
        anchors.verticalCenter: imageContainer.verticalCenter
        wrapMode: Text.WrapAtWordBoundaryOrAnywhere
        width: 200
    }

}
