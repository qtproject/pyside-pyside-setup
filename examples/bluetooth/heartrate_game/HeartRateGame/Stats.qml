// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick
import HeartRateGame

GamePage {
    id: statsPage

    required property DeviceHandler deviceHandler

    Column {
        anchors.centerIn: parent
        width: parent.width

        Rectangle {
            id: resultRect
            anchors.horizontalCenter: parent.horizontalCenter
            width: height
            height: statsPage.height / 2 - GameSettings.fieldHeight
            radius: height / 2
            color: GameSettings.viewColor

            Column {
                anchors.centerIn: parent

                Text {
                    id: resultCaption
                    anchors.horizontalCenter: parent.horizontalCenter
                    width: resultRect.width * 0.8
                    height: resultRect.height * 0.15
                    horizontalAlignment: Text.AlignHCenter
                    fontSizeMode: Text.Fit
                    font.pixelSize: GameSettings.bigFontSize
                    color: GameSettings.textColor
                    text: qsTr("RESULT")
                }

                Text {
                    id: resultValue
                    anchors.horizontalCenter: parent.horizontalCenter
                    width: resultRect.width * 0.8
                    height: resultRect.height * 0.4
                    horizontalAlignment: Text.AlignHCenter
                    fontSizeMode: Text.Fit
                    font.pixelSize: GameSettings.hugeFontSize
                    font.bold: true
                    color: GameSettings.heartRateColor
                    text: (statsPage.deviceHandler.maxHR - statsPage.deviceHandler.minHR).toFixed(0)
                }
            }
        }


        Item {
            height: GameSettings.fieldHeight
            width: 1
        }

        StatsLabel {
            title: qsTr("MIN")
            value: statsPage.deviceHandler.minHR.toFixed(0)
        }

        StatsLabel {
            title: qsTr("MAX")
            value: statsPage.deviceHandler.maxHR.toFixed(0)
        }

        StatsLabel {
            title: qsTr("AVG")
            value: statsPage.deviceHandler.average.toFixed(1)
        }

        StatsLabel {
            title: qsTr("CALORIES")
            value: statsPage.deviceHandler.calories.toFixed(3)
        }
    }
}
