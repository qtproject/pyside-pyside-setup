// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick

Rectangle {
    id: page

    signal buttonClicked
    signal textRotationChanged(double rot)

    width: 500; height: 200
    color: "lightgray"

    Text {
        id: helloText
        text: "Hello world!"
        y: 30
        x: page.width/2-width/2
        font.pointSize: 24; font.bold: true
        onRotationChanged: textRotationChanged(rotation)

        states: State {
            name: "down"; when: buttonMouseArea.pressed === true
            PropertyChanges {
                target: helloText;
                rotation: 180;
                y: 100;
            }
        }

        transitions: Transition {
            from: ""; to: "down"; reversible: true
            ParallelAnimation {
                NumberAnimation {
                    properties: "y,rotation"
                    duration: 500
                    easing.type: Easing.InOutQuad
                }
            }
        }
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
                buttonClicked()
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
