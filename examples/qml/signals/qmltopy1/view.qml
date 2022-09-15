// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause


import QtQuick

import examples.signals.qmltopy1 1.0

Rectangle {
    id: page

    width: 500; height: 200
    color: "lightgray"

    Console {
        id: pyConsole
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
                // once the "console" context has been declared,
                // slots can be called like functions
                pyConsole.outputFloat(123)
                pyConsole.outputStr("foobar")
                pyConsole.output(helloText.x)
                pyConsole.output(helloText.text)
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
