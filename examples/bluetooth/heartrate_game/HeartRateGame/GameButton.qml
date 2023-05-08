// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick

Rectangle {
    id: button
    color: baseColor
    onEnabledChanged: checkColor()
    radius: GameSettings.buttonRadius

    property color baseColor: GameSettings.buttonColor
    property color pressedColor: GameSettings.buttonPressedColor
    property color disabledColor: GameSettings.disabledButtonColor

    signal clicked

    function checkColor() {
        if (!button.enabled) {
            button.color = disabledColor
        } else {
            if (mouseArea.containsPress)
                button.color = pressedColor
            else
                button.color = baseColor
        }
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        onPressed: button.checkColor()
        onReleased: button.checkColor()
        onClicked: {
            button.checkColor()
            button.clicked()
        }
    }
}
