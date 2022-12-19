// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick
import CustomGeometry

Item {
    width: 300
    height: 200

    BezierCurve {
        id: line
        anchors.fill: parent
        anchors.margins: 20
        property real t
        SequentialAnimation on t {
            NumberAnimation { to: 1; duration: 2000; easing.type: Easing.InOutQuad }
            NumberAnimation { to: 0; duration: 2000; easing.type: Easing.InOutQuad }
            loops: Animation.Infinite
        }

        p2: Qt.point(t, 1 - t)
        p3: Qt.point(1 - t, t)
    }

    Text {
        anchors.bottom: line.bottom
        x: 20
        width: parent.width - 40
        wrapMode: Text.WordWrap

        text: "This curve is a custom scene graph item, implemented using GL_LINE_STRIP"
    }
}
