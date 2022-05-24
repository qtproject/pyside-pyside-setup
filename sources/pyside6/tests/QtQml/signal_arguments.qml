// Copyright (C) 2019 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0


import QtQuick 2.5
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.2
import test.Obj 1.0

Rectangle {
    visible: true
    required property Obj o
    GridLayout {
        Button {
            id: button
            objectName: "button"
            text: "sum!"
            onClicked: {
                o.sum(40, 2)
            }
        }
        Text {
            id: sumResultText
        }
    }
    Connections {
        target: o
        function onSumResult(sum) {
            // set the value on the Qml side
            sumResultText.text = sum
            // set internal Python value from the already
            // modified value
            o.sendValue(sumResultText.text)
        }
    }
}
