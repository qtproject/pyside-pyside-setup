// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick
import QtQml

import examples.signals.pytoqml2 1.0

Rectangle {
    id: page

    width: 500; height: 200
    color: "lightgray"
    required property RotateValue rotatevalue

    Text {
        id: helloText
        text: "Hello world!"
        anchors.horizontalCenter: page.horizontalCenter
        y: 30
        font.pointSize: 24; font.bold: true
    }

    Connections {
        target: rotatevalue
        function onValueChanged(val) {
            helloText.rotation = val
        }
    }
}
