// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick

import examples.signals.qmltopy2 1.0

Rectangle {
    id: page

    width: 500; height: 200
    color: "lightgray"

    RotateValue {
        id: rotatevalue
    }

    Text {
        id: helloText
        text: "Hello world!"
        anchors.horizontalCenter: page.horizontalCenter
        y: 30
        font.pointSize: 24; font.bold: true
    }


    Rectangle {
        id: button
        width: 150; height: 40
        color: "darkgray"
        anchors.horizontalCenter: page.horizontalCenter
        y: 120
        MouseArea {
            id: buttonMouseArea
            objectName: "buttonMouseArea"
            anchors.fill: parent
            onClicked: {
                helloText.rotation = rotatevalue.val()
            }
        }
        Text {
            id: buttonText
            text: "Press me!"
            anchors.horizontalCenter: button.horizontalCenter
            anchors.verticalCenter: button.verticalCenter
            font.pointSize: 16
        }
    }
}
