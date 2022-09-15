// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick

Rectangle {
    id: page

    function updateRotater() {
        rotater.angle = rotater.angle + 45
    }

    width: 500; height: 200
    color: "lightgray"

    Rectangle {
        id: rotater
        property real angle : 0
        x: 240
        width: 100; height: 10
        color: "black"
        y: 95

        transform: Rotation {
            origin.x: 10; origin.y: 5
            angle: rotater.angle
            Behavior on angle {
                SpringAnimation {
                    spring: 1.4
                    damping: .05
                }
            }
        }
    }

}
