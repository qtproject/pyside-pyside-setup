// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick

GamePage {

    Column {
        anchors.centerIn: parent
        width: parent.width

        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            font.pixelSize: GameSettings.hugeFontSize
            color: GameSettings.textColor
            text: qsTr("RESULT")
        }

        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            font.pixelSize: GameSettings.giganticFontSize*3
            color: GameSettings.textColor
            text: (deviceHandler.maxHR - deviceHandler.minHR).toFixed(0)
        }

        Item {
            height: GameSettings.fieldHeight
            width: 1
        }

        StatsLabel {
            title: qsTr("MIN")
            value: deviceHandler.minHR.toFixed(0)
        }

        StatsLabel {
            title: qsTr("MAX")
            value: deviceHandler.maxHR.toFixed(0)
        }

        StatsLabel {
            title: qsTr("AVG")
            value: deviceHandler.average.toFixed(1)
        }


        StatsLabel {
            title: qsTr("CALORIES")
            value: deviceHandler.calories.toFixed(3)
        }
    }
}
